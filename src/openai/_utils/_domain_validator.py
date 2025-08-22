# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import re
from typing import List, Optional
from typing_extensions import Literal

__all__ = ["DomainValidator"]


class DomainValidator:
    """Utility class for validating domain formats."""
    
    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    
    WILDCARD_DOMAIN_PATTERN = re.compile(
        r'^\*(?:\.(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,})?$'
    )
    
    @classmethod
    def validate_domain(cls, domain: str) -> bool:
        """Validate a single domain format.
        
        Args:
            domain: The domain to validate (e.g., "example.com" or "*.example.com")
            
        Returns:
            True if the domain format is valid, False otherwise
        """
        if not domain or not isinstance(domain, str):
            return False
            
        # Check for wildcard domains
        if domain.startswith('*.'):
            return bool(cls.WILDCARD_DOMAIN_PATTERN.match(domain))
        
        # Check for regular domains
        return bool(cls.DOMAIN_PATTERN.match(domain))
    
    @classmethod
    def validate_domains(cls, domains: List[str]) -> List[str]:
        """Validate a list of domains and return only valid ones.
        
        Args:
            domains: List of domains to validate
            
        Returns:
            List of valid domains
        """
        if not domains:
            return []
            
        valid_domains = []
        for domain in domains:
            if cls.validate_domain(domain):
                valid_domains.append(domain)
        
        return valid_domains