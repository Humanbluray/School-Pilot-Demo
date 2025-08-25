from postgrest import AsyncPostgrestClient
from services.supabase_client import *
import asyncio
import httpx
from typing import List, Dict
import random

# HEADERS = {"apikey": key, "Authorization": f"Bearer {key}"}
SCHOOL_CODE = 'LBA'

def get_current_year_label():
    resp = supabase_client.table('years').select('name').eq('active', True).single().execute()
    return resp.data['name']


def get_current_year_short():
    resp = supabase_client.table('years').select('short').eq('active', True).single().execute()
    return resp.data['short']



def get_current_year_id():
    resp = supabase_client.table('years').select('id').eq('active', True).single().execute()
    return resp.data['id']


def get_new_registration_number():
    return f"{school_code}{random.randint(1000, 9999)}"


def get_amount_paid_by_student_id(student_id):
    resp = supabase_client.table('school_fees').select('amount').eq(
        'student_id', student_id
    ).eq('year_id', get_current_year_id()).execute()

    amount = 0
    if resp.data:
        for row in resp.data:
            amount += row['amount']

    return amount


def get_all_payments_by_student(student_id):
    resp = supabase_client.table('school_fees').select('*').eq(
        'student_id', student_id
    ).eq('year_id', get_current_year_id()).execute()

    return resp.data


def total_school_fees():
    resp = (supabase_client.table('fees_part').select('amount').eq(
        'year_id', get_current_year_id()).neq('part', 'inscription').execute())

    amount = 0
    if resp.data:
        for row in resp.data:
            amount += row['amount']

    return amount


def get_student_name_by_id(student_id):
    resp = supabase_client.table('students').select('*').eq('id', student_id).single().execute()
    return f"{resp.data['name']} {resp.data['surname']}"

# async functions...
async def get_active_year_id(access_token) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/years?active=eq.true&select=id",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
        )
        data = response.json()
        return data[0]['id'] if data else None


async def get_students_with_details(access_token) -> List[dict]:
    year_id = await get_active_year_id(access_token)
    # print(year_id)
    if not year_id:
        return []

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/registrations",
            params={
                "select": "id,receipt_url,amount,student_id(id,name,surname,registration_number,image_url,gender),class_id(id,code),year_id(id,name)",
                "year_id": f"eq.{year_id}"
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
        )
        response.raise_for_status()
        data = response.json()

        return [
            {
                "registration_id": item["id"],
                "receipt_url": item["receipt_url"],
                "amount": item.get("amount"),
                "student_id": item["student_id"]["id"] if item.get("student_id") else None,
                "image_url": item["student_id"]["image_url"] if item.get("student_id") else None,
                "gender": item["student_id"]["gender"] if item.get("student_id") else None,
                "name": item["student_id"]["name"] if item.get("student_id") else None,
                "surname": item["student_id"]["surname"] if item.get("student_id") else None,
                "registration_number": item['student_id']['registration_number'] if item.get('student_id') else None,
                "class_id": item["class_id"]["id"] if item.get("class_id") else None,
                "class_code": item["class_id"]["code"] if item.get("class_id") else None,
                "year_id": item["year_id"]["id"] if item.get("year_id") else None,
                "year_name": item["year_id"]["name"] if item.get("year_id") else None,
            }
            for item in data
        ]


async def get_unregistered_students(access_token: str) -> List[dict]:
    # get active year
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return []

    # get ids of registered students
    async with httpx.AsyncClient() as client:
        registrations_resp = await client.get(
            f"{url}/rest/v1/registrations?year_id=eq.{year_id}&select=student_id",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        registrations_data = registrations_resp.json()
        registered_ids = [item["student_id"] for item in registrations_data if item["student_id"]]

    # if no student registered we take all of them
    if not registered_ids:
        query = f"{url}/rest/v1/students?select=id,name,surname"
    else:
        ids_str = ",".join(f'"{id}"' for id in registered_ids)  # Format pour Supabase `not.in`
        query = f"{url}/rest/v1/students?select=id,name,surname&id=not.in.({ids_str})"

    # Étape 3 : récupérer les étudiants non inscrits
    async with httpx.AsyncClient() as client:
        response = await client.get(
            query,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        data = response.json()
        return data


async def get_active_classes(access_token: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes?active=eq.true&select=id,code",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        data = response.json()
        return data


async def get_fee_amount_by_part_and_year(part: str, access_token: str) -> float | None:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/fees_part",
            params={
                "select": "amount",
                "part": f"eq.{part}",
                "year_id": f"eq.{year_id}",
                "limit": 1
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0].get("amount")
        return None


async def get_class_code_by_id_async(class_id: str, access_token: str) -> str | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/classes",
            params={
                "select": "code",
                "id": f"eq.{class_id}",
                "limit": 1
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0].get("code")
        return None


async def get_profile_picture_rate_async(access_token: str) -> float:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return 0.0

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/registrations",
            params={
                "select": "student_id(image_url)",
                "year_id": f"eq.{year_id}"
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()

        total = len(data)
        with_image = sum(1 for item in data if item.get("student_id", {}).get("image_url"))

        return round((with_image / total * 100), 2) if total else 0.0


async def get_total_registered_students_async(access_token: str) -> int:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return 0

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/registrations",
            params={
                "select": "id",
                "year_id": f"eq.{year_id}"
            },
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()
        return len(data)


async def get_student_payments_for_active_year(access_token: str, student_id: str) -> List[dict]:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return []

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/school_fees",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "part,amount,date",
                "year_id": f"eq.{year_id}",
                "student_id": f"eq.{student_id}",
                "order": "date.desc"
            }
        )
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Erreur {res.status_code}: {res.text}")
            return []


async def get_total_school_fees_for_active_year(access_token: str) -> int:
    year_id = await get_active_year_id(access_token)
    if not year_id:
        return 0

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{url}/rest/v1/fees_part",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": key,
                "Accept": "application/json"
            },
            params={
                "select": "amount",
                "year_id": f"eq.{year_id}",
                "part": "not.eq.inscription"
            }
        )
        if res.status_code == 200:
            data = res.json()
            total = sum(item["amount"] for item in data)
            return total
        else:
            print(f"Erreur {res.status_code}: {res.text}")
            return 0


async def get_all_classes_basic_info(access_token: str) -> List[Dict]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key
    }

    url_request = (
        f"{url}/rest/v1/classes"
        f"?select=id,code,level_id"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url_request, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data  # Liste de dictionnaires avec id, code, level_id


async def get_registered_students(access_token: str, year_id: str) -> List[dict]:
    """
    Retourne les id, name, surname des élèves inscrits pour une année donnée.
    """
    request_url = (
        f"{url}/rest/v1/students"
        f"?select=id,name,surname,registrations!inner(year_id)"
        f"&registrations.year_id=eq.{year_id}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        return response.json()


async def insert_discipline_entry(access_token: str, data: dict) -> dict:
    """
    Insère une ligne dans la table 'discipline' à partir d’un dictionnaire de données.
    Le dictionnaire 'data' doit contenir les clés : year_id, student_id, type, quantity.
    """
    request_url = f"{url}/rest/v1/discipline"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=data
        )
        response.raise_for_status()
        return response.json()[0]







