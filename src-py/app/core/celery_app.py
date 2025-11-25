from celery import Celery

# URL FIXA com 127.0.0.1
REDIS_URL_FIXA = "redis://127.0.0.1:6379/0"

celery_app = Celery(
    "trucar_worker",
    broker=REDIS_URL_FIXA,
    backend=REDIS_URL_FIXA,
    # --- CORREÇÃO AQUI ---
    # Adicionamos a lista de módulos que contêm tarefas (@celery_app.task)
    # Se criar mais arquivos de tarefas no futuro, adicione aqui (ex: "app.tasks.fuel_tasks")
    include=["app.tasks.email_tasks"]
    # ---------------------
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
)