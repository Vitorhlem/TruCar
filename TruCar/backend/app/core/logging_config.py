import logging
import sys
import structlog

def setup_logging():
    """
    Configura o logging estruturado para toda a aplicação.
    """
    # Processadores compartilhados para todos os loggers
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Configuração do structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configuração do handler para formatar em JSON
    json_handler = logging.StreamHandler(sys.stdout)
    json_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
    )
    json_handler.setFormatter(json_formatter)

    # Configura o logger raiz para usar nosso handler JSON
    root_logger = logging.getLogger()
    root_logger.addHandler(json_handler)
    root_logger.setLevel(logging.INFO)

    # Silencia outros loggers para não duplicar mensagens
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = [json_handler]
        logger.propagate = False