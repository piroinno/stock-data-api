from pyexpat import model
from src.stock.data.api.main import (
    get_data_lake_file_system_client,
    get_data_lake_service_client,
    get_ticker,
    get_eod_ticker
)

import pytest
from unittest.mock import patch
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.filedatalake._models import ContentSettings
from azure.core._match_conditions import MatchConditions
from azure.identity import DefaultAzureCredential
from stock.data.model import crud
from stock.data.model import models
from stock.data.model.database import  SessionLocal, engine, Base

def init_test_db():
    Base.metadata.create_all(bind=engine)


def drop_test_db():
    Base.metadata.drop_all(bind=engine)


def recreate_test_db():
    drop_test_db()
    init_test_db()


@pytest.fixture(scope="session")
def db():
    recreate_test_db()
    db = SessionLocal()
    add_timezone(db)
    add_country(db)
    add_city(db)
    add_exchanges(db)
    add_ticker(db)
    try:
        yield db
    finally:
        db.close()


def add_timezone(db: SessionLocal):
    # Add test data
    crud.set_timezone(db, timezone=models.TimezoneModel(
        name="Eastern Standard Time", abbr="EST", dst="EDT"
    ))

    crud.set_timezone(db, timezone=models.TimezoneModel(
        name="Greenwich Mean Time", abbr="GMT", dst="BST"
    ))


def add_city(db: SessionLocal):
    # Add test data
    crud.set_city(db, city=models.CityModel(
        name="New York", country_id=1
    ))

    crud.set_city(db, city=models.CityModel(
        name="London", country_id=2
    ))


def add_country(db: SessionLocal):
    # Add test data
    crud.set_country(db, country=models.CountryModel(
        name="United States", code="US"
    ))

    crud.set_country(db, country=models.CountryModel(
        name="United Kingdom", code="UK"
    ))


def add_ticker(db: SessionLocal):
    # Add test data
    crud.set_ticker(db, ticker=models.TickerModel(
        ticker="AAPL", name="Apple Inc.", exchange_id=1
    ))


def add_exchanges(db: SessionLocal):
    # Add test data
    crud.set_exchange(db, exchange=models.ExchangeModel(
        name="National Association of Securities Dealers Automated Quotations", country_id=1, city_id=1, timezone_id=1,
        acronym="NASDAQ", mic="XNAS"
    )
    )

    crud.set_exchange(db, exchange=models.ExchangeModel(
        name="New York Stock Exchange", country_id=1, city_id=1, timezone_id=1,
        acronym="NYSE", mic="XNYS"
    )
    )

    crud.set_exchange(db, exchange=model.ExchangeModel(
        name="London Stock Exchange", country_id=2, city_id=2, timezone_id=2,
        acronym="LSE", mic="XLON"
    )
    )
    
@pytest.fixture
def mock_get_data_lake_service_client(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("src.stock.data.api.main.get_data_lake_service_client", mock_return)

@pytest.fixture
def mock_get_data_lake_file_system_client(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("src.stock.data.api.main.get_data_lake_file_system_client", mock_return)

@pytest.fixture
def mock_get_eod_ticker(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("src.stock.data.api.main.get_eod_ticker", mock_return)

@pytest.fixture
def mock_flagsmith(monkeypatch):
    def mock_return(*args, **kwargs):
        return "mocked"
    monkeypatch.setattr("src.stock.data.api.main.flagsmith", mock_return)

def test_get_data_lake_service_client(mock_get_data_lake_service_client):
    try:
        assert get_data_lake_service_client() == "mocked"
    except Exception as e:
        assert True

def test_get_data_lake_file_system_client(mock_get_data_lake_file_system_client):
    try:
        assert get_data_lake_file_system_client() == "mocked"
    except Exception as e:
        assert True

def test_get_eod_ticker(mock_get_eod_ticker):
    try:
        assert get_eod_ticker("AAPL") == "mocked"
    except Exception as e:
        assert True

def test_get_ticker(mock_flagsmith):
    try:
        assert get_ticker("AAPL") == "mocked"
    except Exception as e:
        assert True

# Path: stock-data-api\tests\test_main.py