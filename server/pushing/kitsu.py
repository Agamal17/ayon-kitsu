from typing import Literal

import httpx


class KitsuLoginException(Exception):
    pass


class Kitsu:
    LoginException = KitsuLoginException

    def __init__(self, server: str, email: str, password: str):
        self.email = email
        self.password = password
        self.base_url = server
        self.token = None

    async def login(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    data={"email": self.email, "password": self.password},
                )
        except httpx.HTTPError as e:
            raise KitsuLoginException("Could not login to Kitsu (server error)") from e

        token = response.json().get("access_token")
        if not token:
            raise KitsuLoginException("Could not login to Kitsu (invalid credentials)")
        self.token = token

    async def logout(self):
        if not self.token:
            return
        async with httpx.AsyncClient() as client:
            await client.get(
                f"{self.base_url}/api/auth/logout",
                headers={"Authorization": f"Bearer {self.token}"},
            )

    async def ensure_login(self):
        if not self.token:
            await self.login()
        else:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/api/auth/authenticated",
                        headers={"Authorization": f"Bearer {self.token}"},
                    )
                    response.raise_for_status()
            except httpx.HTTPError as e:
                status_code = response.status_code
                if status_code == 401:
                    await self.logout()
                    await self.login()

                else:
                    raise KitsuLoginException(
                        "Could not login to Kitsu (server error)"
                    ) from e

            else:
                return

    async def request(
        self,
        method: Literal["get", "post", "put", "delete", "patch"],
        endpoint: str,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> dict:
        await self.ensure_login()
        if headers is None:
            headers = {}
        headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.request(
                method,
                f"{self.base_url}/api/{endpoint}",
                headers=headers,
                **kwargs,
            )
        return response.json()

    async def get(self, endpoint: str, **kwargs) -> dict:
        return await self.request("get", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> dict:
        return await self.request("post", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> dict:
        return await self.request("put", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> dict:
        return await self.request("delete", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> dict:
        return await self.request("patch", endpoint, **kwargs)
