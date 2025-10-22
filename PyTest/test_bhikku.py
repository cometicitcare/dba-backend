# tests/api/v1/test_bhikkus.py
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.models.bhikku import Bhikku
from app.models.user import UserAccount
from app.schemas.bhikku import CRUDAction


@pytest.fixture
def mock_current_user():
    """Mock authenticated user"""
    user = Mock(spec=UserAccount)
    user.ua_user_id = "UA0000001"
    user.ua_session_id = "test_session_123"
    user.ua_username = "admin"
    return user


@pytest.fixture
def auth_headers(mock_current_user):
    """Authentication headers"""
    return {"Authorization": f"Bearer {mock_current_user.ua_session_id}"}


@pytest.fixture
def sample_bhikku_data():
    """Sample valid Bhikku data matching Postman collection"""
    return {
        "br_regn": None,  # Auto-generated
        "br_reqstdate": "2024-01-01",
        "br_gndiv": "GN001",
        "br_currstat": "ACT",
        "br_parshawaya": "PR001",
        "br_livtemple": "LT001",
        "br_mahanatemple": "MT001",
        "br_mahanaacharyacd": "MA001",
        "br_mahananame": "Chief Monk",
        "br_mahanadate": "2022-01-01",
        "br_mobile": "0711234567"
    }


@pytest.fixture
def complete_bhikku_data():
    """Complete Bhikku data with all fields"""
    return {
        "br_regn": None,
        "br_reqstdate": "2024-01-01",
        "br_birthpls": "Colombo",
        "br_province": "Western",
        "br_district": "Colombo",
        "br_korale": "Korale1",
        "br_pattu": "Pattu1",
        "br_division": "Division1",
        "br_vilage": "Village1",
        "br_gndiv": "GN001",
        "br_gihiname": "John Doe",
        "br_dofb": "1990-05-15",
        "br_fathrname": "Father Doe",
        "br_remarks": "Test remarks",
        "br_currstat": "ACT",
        "br_effctdate": "2023-01-01",
        "br_parshawaya": "PR001",
        "br_livtemple": "LT001",
        "br_mahanatemple": "MT001",
        "br_mahanaacharyacd": "MA001",
        "br_multi_mahanaacharyacd": "MA001,MA002",
        "br_mahananame": "Chief Monk",
        "br_mahanadate": "2022-01-01",
        "br_cat": "CAT01",
        "br_mobile": "0711234567",
        "br_email": "test@example.com",
        "br_fathrsaddrs": "123 Test Street, Colombo",
        "br_fathrsmobile": "0771234567",
        "br_upasampada_serial_no": "UPS2024001"
    }


@pytest.fixture
def created_bhikku(db: Session, sample_bhikku_data):
    """Create a Bhikku record for testing"""
    bhikku_data = sample_bhikku_data.copy()
    bhikku_data["br_regn"] = "BH2025000010"
    bhikku_data["br_created_by"] = "UA0000001"
    
    bhikku = Bhikku(**bhikku_data)
    db.add(bhikku)
    db.commit()
    db.refresh(bhikku)
    return bhikku


class TestBhikkuCreate:
    """Tests for CREATE action"""

    def test_create_bhikku_success(self, client: TestClient, db: Session, 
                                   auth_headers, sample_bhikku_data, mock_current_user):
        """Test successful Bhikku creation with minimal required fields"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {
                        "data": sample_bhikku_data
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Bhikku created successfully."
        assert data["data"]["br_regn"].startswith("BH2025")
        assert len(data["data"]["br_regn"]) == 12
        assert data["data"]["br_gndiv"] == "GN001"
        assert data["data"]["br_currstat"] == "ACT"
        assert data["data"]["br_is_deleted"] is False
        assert data["data"]["br_version_number"] == 1

    def test_create_bhikku_with_all_fields(self, client: TestClient, 
                                          auth_headers, complete_bhikku_data, mock_current_user):
        """Test creating Bhikku with all optional fields populated"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": complete_bhikku_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["br_gihiname"] == "John Doe"
        assert data["data"]["br_fathrname"] == "Father Doe"
        assert data["data"]["br_email"] == "test@example.com"
        assert data["data"]["br_province"] == "Western"
        assert data["data"]["br_upasampada_serial_no"] == "UPS2024001"

    def test_create_bhikku_auto_generate_regn(self, client: TestClient, 
                                              auth_headers, sample_bhikku_data, mock_current_user):
        """Test that br_regn is auto-generated when null"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": sample_bhikku_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        regn = data["data"]["br_regn"]
        assert regn is not None
        assert len(regn) == 12
        assert regn.startswith(f"BH{datetime.now().year}")
        # Format should be BH2025000010 or higher
        sequence = int(regn[6:])
        assert sequence >= 10

    def test_create_bhikku_duplicate_regn(self, client: TestClient, created_bhikku,
                                         auth_headers, sample_bhikku_data, mock_current_user):
        """Test creating Bhikku with duplicate registration number"""
        duplicate_data = sample_bhikku_data.copy()
        duplicate_data["br_regn"] = created_bhikku.br_regn
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": duplicate_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("already exists" in str(err).lower() for err in detail)

    def test_create_bhikku_missing_required_fields(self, client: TestClient, 
                                                   auth_headers, mock_current_user):
        """Test creating Bhikku without required fields"""
        incomplete_data = {
            "br_reqstdate": "2024-01-01"
            # Missing: br_gndiv, br_currstat, br_parshawaya, br_livtemple, 
            # br_mahanatemple, br_mahanaacharyacd
        }
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": incomplete_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_create_bhikku_invalid_email(self, client: TestClient, auth_headers, 
                                        complete_bhikku_data, mock_current_user):
        """Test creating Bhikku with invalid email format"""
        invalid_data = complete_bhikku_data.copy()
        invalid_data["br_email"] = "invalid-email-format"
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": invalid_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_create_bhikku_invalid_mobile_length(self, client: TestClient, auth_headers, 
                                                 sample_bhikku_data, mock_current_user):
        """Test creating Bhikku with mobile number exceeding 10 characters"""
        invalid_data = sample_bhikku_data.copy()
        invalid_data["br_mobile"] = "07112345678901"  # Too long
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": invalid_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_create_bhikku_without_data_payload(self, client: TestClient, 
                                               auth_headers, mock_current_user):
        """Test CREATE action without data payload"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("data" in str(err).lower() for err in detail)

    def test_create_bhikku_without_authentication(self, client: TestClient, sample_bhikku_data):
        """Test creating Bhikku without authentication"""
        response = client.post(
            "/api/v1/bhikkus/manage",
            json={
                "action": "CREATE",
                "payload": {"data": sample_bhikku_data}
            }
        )
        
        assert response.status_code in [401, 403]


class TestBhikkuReadOne:
    """Tests for READ_ONE action"""

    def test_read_one_bhikku_success(self, client: TestClient, created_bhikku,
                                     auth_headers, mock_current_user):
        """Test retrieving a single Bhikku by registration number"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ONE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Bhikku retrieved successfully."
        assert data["data"]["br_regn"] == created_bhikku.br_regn
        assert data["data"]["br_id"] == created_bhikku.br_id
        assert data["data"]["br_gndiv"] == created_bhikku.br_gndiv

    def test_read_one_bhikku_not_found(self, client: TestClient, auth_headers, mock_current_user):
        """Test retrieving non-existent Bhikku"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ONE",
                    "payload": {
                        "br_regn": "BH2025999999"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_read_one_bhikku_missing_regn(self, client: TestClient, auth_headers, mock_current_user):
        """Test READ_ONE without br_regn"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ONE",
                    "payload": {}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("br_regn" in str(err).lower() for err in detail)


class TestBhikkuReadAll:
    """Tests for READ_ALL action"""

    def test_read_all_bhikkus_default_pagination(self, client: TestClient, created_bhikku,
                                                 auth_headers, mock_current_user):
        """Test listing Bhikkus with default pagination"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": ""
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Bhikkus retrieved successfully."
        assert isinstance(data["data"], list)
        assert data["totalRecords"] >= 1
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_read_all_bhikkus_with_search(self, client: TestClient, created_bhikku,
                                         auth_headers, mock_current_user):
        """Test searching Bhikkus by registration number"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": created_bhikku.br_regn
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) >= 1
        assert any(b["br_regn"] == created_bhikku.br_regn for b in data["data"])

    def test_read_all_bhikkus_search_by_name(self, client: TestClient, db: Session,
                                            auth_headers, complete_bhikku_data, mock_current_user):
        """Test searching Bhikkus by name"""
        # Create a bhikku with specific name
        bhikku_data = complete_bhikku_data.copy()
        bhikku_data["br_gihiname"] = "Unique Test Name"
        bhikku_data["br_regn"] = "BH2025000020"
        bhikku_data["br_created_by"] = "UA0000001"
        
        bhikku = Bhikku(**bhikku_data)
        db.add(bhikku)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": "Unique Test"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        assert any("Unique Test Name" in b["br_gihiname"] for b in data["data"] if b["br_gihiname"])

    def test_read_all_bhikkus_custom_pagination(self, client: TestClient, db: Session,
                                               auth_headers, sample_bhikku_data, mock_current_user):
        """Test custom pagination parameters"""
        # Create multiple bhikkus
        for i in range(15):
            bhikku_data = sample_bhikku_data.copy()
            bhikku_data["br_regn"] = f"BH2025{str(100 + i).zfill(6)}"
            bhikku_data["br_created_by"] = "UA0000001"
            bhikku = Bhikku(**bhikku_data)
            db.add(bhikku)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 5,
                        "page": 1,
                        "search_key": ""
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5
        assert data["limit"] == 5
        assert data["totalRecords"] >= 15

    def test_read_all_bhikkus_page_based_pagination(self, client: TestClient, db: Session,
                                                    auth_headers, sample_bhikku_data, mock_current_user):
        """Test page-based pagination"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            # Get page 2
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "limit": 5,
                        "page": 2,
                        "search_key": ""
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 5

    def test_read_all_bhikkus_empty_search(self, client: TestClient, auth_headers, mock_current_user):
        """Test search with empty string returns all records"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": ""
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "totalRecords" in data

    def test_read_all_bhikkus_no_results(self, client: TestClient, auth_headers, mock_current_user):
        """Test search with no matching results"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": "NONEXISTENT_SEARCH_TERM_XYZ123"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["totalRecords"] == 0


class TestBhikkuUpdate:
    """Tests for UPDATE action"""

    def test_update_bhikku_success(self, client: TestClient, created_bhikku,
                                   auth_headers, mock_current_user):
        """Test successful Bhikku update"""
        update_data = {
            "br_gihiname": "Updated Lay Name",
            "br_fathrname": "Updated Father"
        }
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn,
                        "data": update_data
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Bhikku updated successfully."
        assert data["data"]["br_gihiname"] == "Updated Lay Name"
        assert data["data"]["br_fathrname"] == "Updated Father"
        assert data["data"]["br_version_number"] > 1

    def test_update_bhikku_partial_fields(self, client: TestClient, created_bhikku,
                                         auth_headers, mock_current_user):
        """Test updating only specific fields"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn,
                        "data": {
                            "br_mobile": "0777654321",
                            "br_email": "updated@example.com"
                        }
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["br_mobile"] == "0777654321"
        assert data["data"]["br_email"] == "updated@example.com"

    def test_update_bhikku_not_found(self, client: TestClient, auth_headers, mock_current_user):
        """Test updating non-existent Bhikku"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": "BH2025999999",
                        "data": {
                            "br_gihiname": "Test"
                        }
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_bhikku_missing_regn(self, client: TestClient, auth_headers, mock_current_user):
        """Test UPDATE without br_regn"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "data": {
                            "br_gihiname": "Test"
                        }
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("br_regn" in str(err).lower() for err in detail)

    def test_update_bhikku_missing_data(self, client: TestClient, created_bhikku,
                                       auth_headers, mock_current_user):
        """Test UPDATE without data payload"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("data" in str(err).lower() for err in detail)

    def test_update_bhikku_invalid_email(self, client: TestClient, created_bhikku,
                                        auth_headers, mock_current_user):
        """Test updating with invalid email"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn,
                        "data": {
                            "br_email": "invalid-email"
                        }
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422


class TestBhikkuDelete:
    """Tests for DELETE action"""

    def test_delete_bhikku_success(self, client: TestClient, created_bhikku,
                                   auth_headers, mock_current_user, db: Session):
        """Test successful Bhikku deletion (soft delete)"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "DELETE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Bhikku deleted successfully."
        assert data["data"] is None
        
        # Verify soft delete
        db.refresh(created_bhikku)
        assert created_bhikku.br_is_deleted is True

    def test_delete_bhikku_not_found(self, client: TestClient, auth_headers, mock_current_user):
        """Test deleting non-existent Bhikku"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "DELETE",
                    "payload": {
                        "br_regn": "BH2025999999"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_bhikku_missing_regn(self, client: TestClient, auth_headers, mock_current_user):
        """Test DELETE without br_regn"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "DELETE",
                    "payload": {}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("br_regn" in str(err).lower() for err in detail)

    def test_delete_already_deleted_bhikku(self, client: TestClient, created_bhikku,
                                          auth_headers, mock_current_user, db: Session):
        """Test deleting already deleted Bhikku"""
        # First delete
        created_bhikku.br_is_deleted = True
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "DELETE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 404


class TestBhikkuInvalidActions:
    """Tests for invalid actions and edge cases"""

    def test_invalid_action(self, client: TestClient, auth_headers, mock_current_user):
        """Test with invalid action type"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "INVALID_ACTION",
                    "payload": {}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_missing_action(self, client: TestClient, auth_headers, mock_current_user):
        """Test request without action field"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "payload": {}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_missing_payload(self, client: TestClient, auth_headers, mock_current_user):
        """Test request without payload field"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL"
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_empty_request_body(self, client: TestClient, auth_headers, mock_current_user):
        """Test with completely empty request body"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={},
                headers=auth_headers
            )
        
        assert response.status_code == 422


class TestBhikkuAuditFields:
    """Tests for audit field handling"""

    def test_create_sets_created_by(self, client: TestClient, db: Session,
                                    auth_headers, sample_bhikku_data, mock_current_user):
        """Test that created_by is set to current user"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": sample_bhikku_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        
        # Fetch from DB to verify audit field
        from app.repositories import bhikku_repo
        bhikku = bhikku_repo.get_by_regn(db, response.json()["data"]["br_regn"])
        assert bhikku.br_created_by == mock_current_user.ua_user_id

    def test_update_sets_updated_by(self, client: TestClient, created_bhikku, db: Session,
                                    auth_headers, mock_current_user):
        """Test that updated_by is set to current user"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn,
                        "data": {"br_gihiname": "Updated"}
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        
        # Fetch from DB to verify audit field
        db.refresh(created_bhikku)
        assert created_bhikku.br_updated_by == mock_current_user.ua_user_id

    def test_version_number_increments_on_update(self, client: TestClient, created_bhikku,
                                                 auth_headers, mock_current_user, db: Session):
        """Test that version number increments on each update"""
        initial_version = created_bhikku.br_version_number
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn,
                        "data": {"br_gihiname": "Updated"}
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        db.refresh(created_bhikku)
        assert created_bhikku.br_version_number == initial_version + 1

    def test_version_number_increments_on_delete(self, client: TestClient, created_bhikku,
                                                 auth_headers, mock_current_user, db: Session):
        """Test that version number increments on delete"""
        initial_version = created_bhikku.br_version_number
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "DELETE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        db.refresh(created_bhikku)
        assert created_bhikku.br_version_number == initial_version + 1


class TestBhikkuSearchFunctionality:
    """Tests for comprehensive search functionality"""

    def test_search_by_mobile(self, client: TestClient, db: Session, complete_bhikku_data,
                              auth_headers, mock_current_user):
        """Test searching by mobile number"""
        bhikku_data = complete_bhikku_data.copy()
        bhikku_data["br_mobile"] = "0719876543"
        bhikku_data["br_regn"] = "BH2025000030"
        bhikku_data["br_created_by"] = "UA0000001"
        
        bhikku = Bhikku(**bhikku_data)
        db.add(bhikku)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": "0719876543"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        assert any(b["br_mobile"] == "0719876543" for b in data["data"])

    def test_search_by_province(self, client: TestClient, db: Session, complete_bhikku_data,
                                auth_headers, mock_current_user):
        """Test searching by province"""
        bhikku_data = complete_bhikku_data.copy()
        bhikku_data["br_province"] = "Central"
        bhikku_data["br_regn"] = "BH2025000031"
        bhikku_data["br_created_by"] = "UA0000001"
        
        bhikku = Bhikku(**bhikku_data)
        db.add(bhikku)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": "Central"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1
        assert any(b["br_province"] == "Central" for b in data["data"])

    def test_search_case_insensitive(self, client: TestClient, db: Session, complete_bhikku_data,
                                     auth_headers, mock_current_user):
        """Test that search is case-insensitive"""
        bhikku_data = complete_bhikku_data.copy()
        bhikku_data["br_gihiname"] = "CaseSensitiveTest"
        bhikku_data["br_regn"] = "BH2025000032"
        bhikku_data["br_created_by"] = "UA0000001"
        
        bhikku = Bhikku(**bhikku_data)
        db.add(bhikku)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": "casesensitive"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1

    def test_search_partial_match(self, client: TestClient, db: Session, complete_bhikku_data,
                                  auth_headers, mock_current_user):
        """Test that search supports partial matching"""
        bhikku_data = complete_bhikku_data.copy()
        bhikku_data["br_gihiname"] = "Venerable Pandit Master"
        bhikku_data["br_regn"] = "BH2025000033"
        bhikku_data["br_created_by"] = "UA0000001"
        
        bhikku = Bhikku(**bhikku_data)
        db.add(bhikku)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "READ_ALL",
                    "payload": {
                        "skip": 0,
                        "limit": 10,
                        "page": 1,
                        "search_key": "Pandit"
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1


class TestBhikkuDateHandling:
    """Tests for date field handling"""

    def test_create_with_valid_dates(self, client: TestClient, auth_headers,
                                     complete_bhikku_data, mock_current_user):
        """Test creating Bhikku with valid date formats"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": complete_bhikku_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["br_reqstdate"] == "2024-01-01"
        assert data["data"]["br_dofb"] == "1990-05-15"
        assert data["data"]["br_mahanadate"] == "2022-01-01"

    def test_create_with_invalid_date_format(self, client: TestClient, auth_headers,
                                            sample_bhikku_data, mock_current_user):
        """Test creating Bhikku with invalid date format"""
        invalid_data = sample_bhikku_data.copy()
        invalid_data["br_reqstdate"] = "01-01-2024"  # Wrong format
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": invalid_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 422

    def test_update_date_fields(self, client: TestClient, created_bhikku,
                               auth_headers, mock_current_user):
        """Test updating date fields"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "UPDATE",
                    "payload": {
                        "br_regn": created_bhikku.br_regn,
                        "data": {
                            "br_dofb": "1995-06-20",
                            "br_effctdate": "2024-01-01"
                        }
                    }
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["br_dofb"] == "1995-06-20"
        assert data["data"]["br_effctdate"] == "2024-01-01"


class TestBhikkuRegistrationNumberGeneration:
    """Tests for registration number auto-generation"""

    def test_regn_format_is_correct(self, client: TestClient, auth_headers,
                                    sample_bhikku_data, mock_current_user):
        """Test that generated registration number has correct format"""
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": sample_bhikku_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        regn = response.json()["data"]["br_regn"]
        
        # Format: BH + YEAR(4) + SEQUENCE(6) = 12 chars
        assert len(regn) == 12
        assert regn[:2] == "BH"
        assert regn[2:6].isdigit()  # Year part
        assert regn[6:].isdigit()   # Sequence part
        assert int(regn[2:6]) == datetime.now().year

    def test_sequential_regn_generation(self, client: TestClient, db: Session,
                                       auth_headers, sample_bhikku_data, mock_current_user):
        """Test that registration numbers are generated sequentially"""
        regns = []
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            for i in range(3):
                response = client.post(
                    "/api/v1/bhikkus/manage",
                    json={
                        "action": "CREATE",
                        "payload": {"data": sample_bhikku_data}
                    },
                    headers=auth_headers
                )
                assert response.status_code == 200
                regns.append(response.json()["data"]["br_regn"])
        
        # Extract sequence numbers
        sequences = [int(regn[6:]) for regn in regns]
        
        # Verify they are sequential
        for i in range(1, len(sequences)):
            assert sequences[i] == sequences[i-1] + 1

    def test_regn_starts_at_10(self, client: TestClient, db: Session, auth_headers,
                              sample_bhikku_data, mock_current_user):
        """Test that sequence starts at 10 for first record of the year"""
        # Clear existing records for current year (if any)
        current_year = datetime.now().year
        db.query(Bhikku).filter(
            Bhikku.br_regn.like(f"BH{current_year}%")
        ).delete(synchronize_session=False)
        db.commit()
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": sample_bhikku_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        regn = response.json()["data"]["br_regn"]
        sequence = int(regn[6:])
        assert sequence >= 10


class TestBhikkuEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_max_length_fields(self, client: TestClient, auth_headers,
                              sample_bhikku_data, mock_current_user):
        """Test maximum length validations"""
        long_data = sample_bhikku_data.copy()
        long_data["br_gihiname"] = "A" * 50  # Max 50 chars
        long_data["br_email"] = "a" * 40 + "@example.com"  # Max 50 chars
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": long_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200

    def test_null_optional_fields(self, client: TestClient, auth_headers,
                                  sample_bhikku_data, mock_current_user):
        """Test that optional fields can be null"""
        minimal_data = {
            "br_reqstdate": "2024-01-01",
            "br_gndiv": "GN001",
            "br_currstat": "ACT",
            "br_parshawaya": "PR001",
            "br_livtemple": "LT001",
            "br_mahanatemple": "MT001",
            "br_mahanaacharyacd": "MA001"
        }
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": minimal_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["br_gihiname"] is None
        assert data["br_email"] is None
        assert data["br_remarks"] is None

    def test_special_characters_in_text_fields(self, client: TestClient, auth_headers,
                                               complete_bhikku_data, mock_current_user):
        """Test handling of special characters in text fields"""
        special_data = complete_bhikku_data.copy()
        special_data["br_gihiname"] = "O'Brien & Sons"
        special_data["br_remarks"] = "Special chars: @#$%^&*()"
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": special_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["br_gihiname"] == "O'Brien & Sons"

    def test_unicode_characters(self, client: TestClient, auth_headers,
                               complete_bhikku_data, mock_current_user):
        """Test handling of Unicode characters (Sinhala, Tamil)"""
        unicode_data = complete_bhikku_data.copy()
        unicode_data["br_gihiname"] = "සිංහල නම"  # Sinhala
        unicode_data["br_fathrname"] = "தமிழ் பெயர்"  # Tamil
        
        with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
            response = client.post(
                "/api/v1/bhikkus/manage",
                json={
                    "action": "CREATE",
                    "payload": {"data": unicode_data}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["br_gihiname"] == "සිංහල නම"
        assert data["br_fathrname"] == "தமிழ் பெயர்"


class TestBhikkuConcurrency:
    """Tests for concurrent operations"""

    def test_concurrent_creates_unique_regn(self, client: TestClient, db: Session,
                                           auth_headers, sample_bhikku_data, mock_current_user):
        """Test that concurrent creates generate unique registration numbers"""
        import concurrent.futures
        
        def create_bhikku():
            with patch('app.api.auth_middleware.get_current_user', return_value=mock_current_user):
                response = client.post(
                    "/api/v1/bhikkus/manage",
                    json={
                        "action": "CREATE",
                        "payload": {"data": sample_bhikku_data}
                    },
                    headers=auth_headers
                )
            return response.json()["data"]["br_regn"] if response.status_code == 200 else None
        
        # Create multiple bhikkus concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_bhikku) for _ in range(3)]
            regns = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Remove None values (if any failed)
        regns = [r for r in regns if r is not None]
        
        # Verify all registration numbers are unique
        assert len(regns) == len(set(regns))