import pytest
from openai._utils import DomainValidator


class TestDomainValidator:
    def test_validate_valid_domains(self):
        """Test validation of valid domain formats."""
        valid_domains = [
            "example.com",
            "sub.example.com",
            "openai.com",
            "arxiv.org",
            "nature.com",
            "*.example.com",
            "*.edu",
            "*.gov"
        ]
        
        for domain in valid_domains:
            assert DomainValidator.validate_domain(domain), f"Domain {domain} should be valid"
    
    def test_validate_invalid_domains(self):
        """Test validation of invalid domain formats."""
        invalid_domains = [
            "",
            "invalid",
            "example..com",
            ".example.com",
            "example.",
            "example.com.",
            "https://example.com",
            "http://example.com",
            "example.com/path",
            "example.com?query=param",
            "*.invalid*",
            "*.",
            "*"
        ]
        
        for domain in invalid_domains:
            assert not DomainValidator.validate_domain(domain), f"Domain {domain} should be invalid"
    
    def test_validate_domains_list(self):
        """Test validation of a list of domains."""
        mixed_domains = [
            "example.com",      # valid
            "invalid",          # invalid
            "openai.com",       # valid
            "https://bad.com",  # invalid
            "*.edu",            # valid
            ""                  # invalid
        ]
        
        expected_valid = ["example.com", "openai.com", "*.edu"]
        actual_valid = DomainValidator.validate_domains(mixed_domains)
        
        assert actual_valid == expected_valid
    
    def test_validate_empty_domains_list(self):
        """Test validation of an empty domains list."""
        assert DomainValidator.validate_domains([]) == []
        assert DomainValidator.validate_domains(None) == []