from fastapi import APIRouter, HTTPException, Path
import httpx

router = APIRouter()

@router.get("/cep/{cep}")
async def get_address_by_cep(
    cep: str = Path(..., title="O CEP para consulta", regex="^[0-9]{8}$")
):
    """
    Consulta um CEP no serviço ViaCEP e retorna os dados do endereço.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://viacep.com.br/ws/{cep}/json/")
            response.raise_for_status()  # Lança um erro para respostas 4xx ou 5xx
            
            data = response.json()
            if data.get("erro"):
                raise HTTPException(status_code=404, detail="CEP não encontrado.")
            
            return {
                "street": data.get("logradouro"),
                "neighborhood": data.get("bairro"),
                "city": data.get("localidade"),
                "state": data.get("uf"),
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Erro ao consultar o serviço de CEP.")
        except Exception:
            raise HTTPException(status_code=500, detail="Erro interno ao processar a solicitação de CEP.")