from fasthtml.common import *
from src.interface.api.auth import get_repository
from src.infrastructure.config import settings
import asyncio
import base64

# Настройка стилей
hdrs = (
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"),
    Script(src="https://cdn.tailwindcss.com"),
)

def auth_before(req):
    auth = req.headers.get('Authorization')
    if not auth: return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="zrelay admin"'})
    
    try:
        scheme, data = auth.split()
        if scheme.lower() != 'basic': return Response(status=401)
        decoded = base64.b64decode(data).decode('utf-8')
        username, password = decoded.split(':')
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            return
    except Exception:
        pass
    return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="zrelay admin"'})

app, rt = fast_app(hdrs=hdrs, cls="p-4", before=auth_before)

def Layout(*args):
    return Main(
        Nav(
            Div(
                A("zrelay Admin", href="/admin", cls="btn btn-ghost text-xl"),
                cls="flex-1"
            ),
            Div(
                Ul(
                    Li(A("Dashboard", href="/admin")),
                    Li(A("Logs", href="/admin/logs")),
                    Li(A("Keys", href="/admin/keys")),
                    cls="menu menu-horizontal px-1"
                ),
                cls="flex-none"
            ),
            cls="navbar bg-base-200 mb-8 rounded-box shadow-lg"
        ),
        Container(*args, cls="mx-auto max-w-6xl"),
        cls="bg-base-100 min-h-screen"
    )

@rt("/admin")
async def index():
    repo = get_repository()
    stats = await repo.get_stats_summary()
    
    return Layout(
        H1("Dashboard", cls="text-3xl font-bold mb-6"),
        Div(
            Div(
                Div("Total Calls", cls="stat-title"),
                Div(str(stats['total_calls']), cls="stat-value text-primary"),
                cls="stat"
            ),
            Div(
                Div("Success Rate", cls="stat-title"),
                Div(f"{int(stats['success_calls']/stats['total_calls']*100) if stats['total_calls'] else 0}%", cls="stat-value text-secondary"),
                cls="stat"
            ),
            Div(
                Div("Avg Duration", cls="stat-title"),
                Div(f"{stats['avg_duration_ms']} ms", cls="stat-value"),
                cls="stat"
            ),
            cls="stats shadow w-full"
        )
    )

@rt("/admin/logs")
async def logs():
    repo = get_repository()
    recent_logs = await repo.get_recent_logs(50)
    
    rows = [
        Tr(
            Td(log.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
            Td(log.tool),
            Td(log.operation),
            Td(Div(cls=f"badge {'badge-success' if log.success else 'badge-error'}", content="OK" if log.success else "ERR")),
            Td(f"{log.duration_ms}ms"),
            Td(log.client_key_id[:8] + "...")
        ) for log in recent_logs
    ]
    
    return Layout(
        H1("Recent Logs", cls="text-3xl font-bold mb-6"),
        Div(
            Table(
                Thead(Tr(Th("Time"), Th("Tool"), Th("Op"), Th("Status"), Th("Lat"), Th("Key"))),
                Tbody(*rows),
                cls="table table-zebra w-full"
            ),
            cls="overflow-x-auto shadow-xl rounded-box"
        )
    )

@rt("/admin/keys")
async def keys():
    repo = get_repository()
    all_keys = await repo.get_all_api_keys()
    
    # Форма создания
    add_form = Form(
        Group(
            Input(name="name", placeholder="Key Name (e.g. My Bot)", cls="input input-bordered"),
            Button("Generate New Key", cls="btn btn-primary"),
        ),
        hx_post="/admin/keys/create",
        hx_target="#keys-list",
        cls="mb-8"
    )
    
    rows = [render_key_row(k) for k in all_keys]
    
    return Layout(
        H1("API Keys", cls="text-3xl font-bold mb-6"),
        add_form,
        Div(
            Table(
                Thead(Tr(Th("Name"), Th("API Key"), Th("Enabled"), Th("Created"), Th("Actions"))),
                Tbody(*rows, id="keys-list"),
                cls="table table-md w-full"
            ),
            cls="overflow-x-auto shadow-xl rounded-box"
        )
    )

def render_key_row(k):
    return Tr(
        Td(k.name, cls="font-semibold"),
        Td(
            Div(
                Code(k.key, cls="text-xs"),
                Button("📋", cls="btn btn-ghost btn-xs", onclick=f"navigator.clipboard.writeText('{k.key}')"),
                cls="flex items-center gap-2"
            )
        ),
        Td(
            Input(type="checkbox", cls="toggle toggle-success", 
                  checked=k.enabled,
                  hx_post=f"/admin/keys/toggle/{k.id}",
                  hx_swap="none")
        ),
        Td(k.created_at.strftime("%Y-%m-%d")),
        Td(
            Button("Delete", 
                   cls="btn btn-error btn-outline btn-xs",
                   hx_delete=f"/admin/keys/delete/{k.id}",
                   hx_confirm="Are you sure?",
                   hx_target="closest tr",
                   hx_swap="outerHTML")
        ),
        id=f"key-{k.id}"
    )

@rt("/admin/keys/create")
async def post(name: str):
    if not name: return ""
    repo = get_repository()
    new_key = await repo.create_api_key(name)
    return render_key_row(new_key)

@rt("/admin/keys/delete/{key_id}")
async def delete(key_id: str):
    repo = get_repository()
    await repo.delete_api_key(key_id)
    return ""

@rt("/admin/keys/toggle/{key_id}")
async def post(key_id: str, request):
    # FastHTML автоматически парсит body. Если чекбокс в форме, он придет. 
    # Но HTMX при нажатии на toggle без формы может не прислать значение.
    # Для простоты в MVP просто инвертируем текущее состояние.
    repo = get_repository()
    # Получаем текущее состояние (можно было бы передать в hx-vals, но так надежнее)
    keys = await repo.get_all_api_keys()
    current = next((k for k in keys if k.id == key_id), None)
    if current:
        await repo.update_api_key_status(key_id, not current.enabled)
    return ""
