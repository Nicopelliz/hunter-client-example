import os
from typing import Any, Dict, Optional
import requests
from dotenv import load_dotenv

import logging
log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

load_dotenv()
API_KEY: str | None = os.getenv("HUNTER_API_KEY")
BASE_URL: str = "https://api.hunter.io/v2/"

SEPARATOR_LENGHT = 50

class HunterClient:
    def __init__(self) -> None:
        # Inizializza il client caricando la chiave API da variabile d'ambiente
        if API_KEY is None:
            raise ValueError("Missing API key")
        self.api_key: str = API_KEY
        self.base_url: str = BASE_URL
        self.session: requests.Session = requests.Session()

    def discover(self, timeout: int = 10, **kwargs: Any) -> Dict[str, Any]:
        return self._request("POST", "discover", timeout, json=kwargs)

    def domain_search(self, timeout: int = 5, **kwargs: Any) -> Dict[str, Any]:
        return self._request("GET", "domain-search", timeout, request_params=kwargs)

    def email_finder(self, timeout: int = 5, **kwargs: Any) -> Dict[str, Any]:
        return self._request("GET", "email-finder", timeout, request_params=kwargs)

    def _make_request(
        self, method: str,
        url: str, timeout: int,
        json: Optional[Dict[str, Any]],
        request_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        response: requests.Response = self.session.request(
            method,
            url,
            timeout=timeout,
            json=json,
            params=request_params,
        )
        response.raise_for_status()
        return response.json()

    def _request(
        self,
        method: str,
        url: str,
        timeout: int,
        request_params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if request_params is None:
            request_params = {}
        if json is None:
            json = {}

        url = self.base_url + url
        if url.endswith("/"):
            url = url[:-1]

        json["api_key"] = self.api_key
        try:
            response = self._make_request(method, url, timeout, json, request_params)
        except requests.exceptions.HTTPError as err:
            return {'Error': f"HTTP error: {err}"}
        except requests.exceptions.RequestException as err:
            return {'Error':f"Other request error: {err}"}
        else:
            return response


# Testing the client
if __name__ == '__main__':
    client = HunterClient()

    # Test Discover
    response = client.discover(query="Companies in Europe in the Tech Industry")
    log.info(response)
    log.info('#' * SEPARATOR_LENGHT)

    # Test Email finder
    response = client.email_finder(
        domain='sorgenia.it', first_name='Sara', last_name='Amata'
    )
    log.info(response)
    log.info('#' * SEPARATOR_LENGHT)

    # Test Domain Search
    response = client.domain_search(domain='reddit.com')
    log.info(response)
    log.info('#' * SEPARATOR_LENGHT)
