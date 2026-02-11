"""
QA tests for db/connection.py and db/operations.py
"""

from unittest.mock import Mock, patch

import pytest


def test_database_connect_success():
    """Database.connect success with mocked MongoClient."""
    with patch("src.db.connection.DatabaseSettings") as mock_settings:
        mock_settings.return_value.DB_URI = "mongodb://localhost:27017"
        with patch("src.db.connection.MongoClient") as mock_mongo:
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_mongo.return_value = mock_client

            from src.db.connection import Database
            db = Database()
            result = db.connect("testdb")

            assert result is mock_db
            mock_mongo.assert_called_once_with("mongodb://localhost:27017")


def test_database_connect_cached():
    """Calling connect twice returns the same cached connection."""
    with patch("src.db.connection.DatabaseSettings") as mock_settings:
        mock_settings.return_value.DB_URI = "mongodb://localhost:27017"
        with patch("src.db.connection.MongoClient") as mock_mongo:
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_mongo.return_value = mock_client

            from src.db.connection import Database
            db = Database()
            result1 = db.connect("testdb")
            result2 = db.connect("testdb")

            assert result1 is result2
            mock_mongo.assert_called_once()


def test_database_connect_failure():
    """Database.connect raises when MongoClient fails."""
    with patch("src.db.connection.DatabaseSettings") as mock_settings:
        mock_settings.return_value.DB_URI = "mongodb://bad:27017"
        with patch("src.db.connection.MongoClient") as mock_mongo:
            mock_mongo.side_effect = Exception("Connection refused")

            from src.db.connection import Database
            db = Database()
            with pytest.raises(Exception, match="Connection refused"):
                db.connect()


def test_database_disconnect():
    """disconnect closes client and resets state."""
    with patch("src.db.connection.DatabaseSettings") as mock_settings:
        mock_settings.return_value.DB_URI = "mongodb://localhost:27017"
        with patch("src.db.connection.MongoClient") as mock_mongo:
            mock_client = Mock()
            mock_db = Mock()
            mock_client.__getitem__ = Mock(return_value=mock_db)
            mock_mongo.return_value = mock_client

            from src.db.connection import Database
            db = Database()
            db.connect()
            db.disconnect()

            mock_client.close.assert_called_once()
            assert db.client is None
            assert db.db is None


def test_database_disconnect_when_not_connected():
    """disconnect when not connected is a no-op."""
    with patch("src.db.connection.DatabaseSettings") as mock_settings:
        mock_settings.return_value.DB_URI = ""

        from src.db.connection import Database
        db = Database()
        db.disconnect()  # Should not raise
        assert db.client is None
        assert db.db is None


def test_insert_report_success():
    """SurfReportDatabaseOps.insert_report success."""
    with patch("src.db.operations.db_manager") as mock_manager:
        mock_collection = Mock()
        mock_collection.insert_one.return_value = Mock(
            inserted_id="abc123"
        )
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_manager.connect.return_value = mock_db

        from src.db.operations import SurfReportDatabaseOps
        ops = SurfReportDatabaseOps()
        result = ops.insert_report({"test": "data"})

        assert result == "abc123"
        mock_collection.insert_one.assert_called_once_with({"test": "data"})


def test_insert_report_failure():
    """SurfReportDatabaseOps.insert_report failure raises."""
    with patch("src.db.operations.db_manager") as mock_manager:
        mock_collection = Mock()
        mock_collection.insert_one.side_effect = Exception("Insert failed")
        mock_db = Mock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        mock_manager.connect.return_value = mock_db

        from src.db.operations import SurfReportDatabaseOps
        ops = SurfReportDatabaseOps()

        with pytest.raises(Exception, match="Insert failed"):
            ops.insert_report({"test": "data"})
