import datetime
import logging

import uvicorn
from dependencies import validate_token
from config import settings
import secure
import pytz
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from flagsmith import Flagsmith
import os, uuid, sys 
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core._match_conditions import MatchConditions
from azure.storage.filedatalake._models import ContentSettings
from stock.data.model import crud
from stock.data.model.database import  SessionLocal
flagsmith = Flagsmith(environment_key=os.getenv("FLAG_SMITH_ENVIRONMENT_KEY"))
flags = flagsmith.get_environment_flags()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(debug=True)
csp = secure.ContentSecurityPolicy().img_src("fastapi.tiangolo.com", "data:").style_src("cdn.jsdelivr.net").script_src("cdn.jsdelivr.net", "'unsafe-inline'").default_src("'self'").frame_ancestors("'none'")
hsts = secure.StrictTransportSecurity().max_age(31536000).include_subdomains()
referrer = secure.ReferrerPolicy().no_referrer()
cache_value = secure.CacheControl().no_cache().no_store().max_age(0).must_revalidate()
x_frame_options = secure.XFrameOptions().deny()

secure_headers = secure.Secure(
    csp=csp,
    hsts=hsts,
    referrer=referrer,
    cache=cache_value,
    xfo=x_frame_options,
)


@app.middleware("http")
async def set_secure_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_origin_url],
    allow_methods=["GET"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    message = str(exc.detail)

    return JSONResponse({"message": message}, status_code=exc.status_code)


@app.get("/", include_in_schema=False)
def docs_redirect():
    # Redirect to the openAPI docs page if endpoint not found (404)
    return RedirectResponse(url='/docs')

@app.exception_handler(404)
def custom_404_handler(_, __):
    return docs_redirect()

@app.get("/eod/ticker/{ticker}", dependencies=[Depends(validate_token)])
def get_ticker(ticker: str):
    # Flag to turn this endpoint / path off in the given environment
    if not flags.is_feature_enabled("ticker_api_enabled"):
        return {"error": "Ticker API is not enabled"}
    return {"ticker": get_eod_ticker(ticker)}


@app.get("/eod/ticker/{ticker}/delta/{days}", dependencies=[Depends(validate_token)])
def get_ticker_delta(ticker: str, days: int):
    # Flag to turn this endpoint / path off in the given environment
    if not flags.is_feature_enabled("delta_api_enabled"):
        return {"error": "Delta API is not enabled"}
    return {"ticker": ticker, "days": days}


def get_data_lake_service_client():
    credential = DefaultAzureCredential()
    adls_service_client = DataLakeServiceClient(
        account_url="{}://{}.dfs.core.windows.net".format(
            "https", os.getenv("STOCK_DATA_STORAGE_ACCOUNT_NAME")
        ),
        credential=credential,
    )
    return adls_service_client


def get_data_lake_file_system_client():
    adls_service_client = get_data_lake_service_client()
    file_system_client = adls_service_client.get_file_system_client(
        file_system=os.getenv("STOCK_DATA_STORAGE_FILE_SYSTEM")
    )
    return file_system_client


def get_eod_ticker(ticker: str):
    db = SessionLocal()
    tickerData = crud.get_ticker(db, ticker=ticker)
    if not tickerData:
        return None
    exchangeData = crud.get_exchange(db, exchange_id=tickerData.exchange_id)
    timezoneData = crud.get_timezone(db, timezone_id=exchangeData.timezone_id)
    date = datetime.datetime.now(pytz.timezone(timezoneData.name)).strftime(
        "%Y-%m-%d"
    )

    file_name = f"{date}/{tickerData.exchange.mic}/{tickerData.ticker}.json"
    logger.info("Getting EOD data for file: {}".format(file_name))
    file_system_client = get_data_lake_file_system_client()
    directory_client = file_system_client.get_directory_client(".")
    file_client = directory_client.get_file_client(file_name)
    try:
        file_client.get_file_properties()
        file = file_client.download_file()
        return file.readall()
    except Exception as e:
        logger.warn("Error getting EOD data for file: {}".format(file_name))
        return None
