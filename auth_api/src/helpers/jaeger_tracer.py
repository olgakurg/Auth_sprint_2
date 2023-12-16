from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from src.core.config import settings

def configure_tracer() -> None:
    resource = Resource(attributes={
        SERVICE_NAME: f'{settings.project_name}'
    })
    trace.set_tracer_provider(TracerProvider(resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )

    if settings.show_traces_console:
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
