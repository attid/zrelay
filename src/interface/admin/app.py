from fasthtml.common import *
from src.interface.api.auth import get_repository
from src.infrastructure.config import settings
import asyncio

# Настройка стилей
hdrs = (
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css"),
    Script(src="https://cdn.tailwindcss.com"),
)

# Инициализируем приложение с поддержкой сессий
app, rt = fast_app(
    hdrs=hdrs, 
    cls="p-4",
    secret_key=settings.ADMIN_PASSWORD # Используем пароль как ключ для подписи сессий
)

def auth_before(req, session):
    # Разрешаем доступ к странице логина без авторизации
    if req.url.path in ['/admin/login', '/admin/logout']: return
    
    # Проверяем наличие флага в сессии
    if not session.get('auth'): 
        return Redirect('/admin/login')

# Применяем проверку ко всем роутам админки
app.before = auth_before

def Layout(*args, active_tab="dashboard"):
    return Main(
        Nav(
            Div(
                A("zrelay Admin", href="/admin", cls="btn btn-ghost text-xl"),
                cls="flex-1"
            ),
            Div(
                Ul(
                    Li(A("Dashboard", href="/admin", cls="active" if active_tab=="dashboard" else "")),
                    Li(A("Logs", href="/admin/logs", cls="active" if active_tab=="logs" else "")),
                    Li(A("Keys", href="/admin/keys", cls="active" if active_tab=="keys" else "")),
                    Li(A("Logout", href="/admin/logout", cls="text-error")),
                    cls="menu menu-horizontal px-1"
                ),
                cls="flex-none"
            ),
            cls="navbar bg-base-200 mb-8 rounded-box shadow-lg"
        ),
        Container(*args, cls="mx-auto max-w-6xl"),
        cls="bg-base-100 min-h-screen"
    )

@rt("/admin/login")
def get():
    return Title("Login - zrelay"), Main(
        Div(
            Div(
                H1("zrelay Login", cls="text-2xl font-bold text-center mb-6"),
                Form(
                    Div(
                        Label("Username", cls="label"),
                        Input(name="username", value="admin", cls="input input-bordered", readonly=True),
                        cls="form-control"
                    ),
                    Div(
                        Label("Password", cls="label"),
                        Input(name="password", type="password", placeholder="Enter admin password", cls="input input-bordered", autofocus=True),
                        cls="form-control mt-4"
                    ),
                    Button("Sign In", cls="btn btn-primary w-full mt-8"),
                    action="/admin/login", method="post"
                ),
                cls="card-body"
            ),
            cls="card w-96 bg-base-200 shadow-xl"
        ),
        cls="flex items-center justify-center min-h-screen bg-base-100"
    )

@rt("/admin/login")
async def post(username: str, password: str, session):
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        session['auth'] = True
        return Redirect('/admin')
    return Redirect('/admin/login?error=1')

@rt("/admin/logout")
def get(session):
    session.pop('auth', None)
    return Redirect('/admin/login')

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
        ),
        active_tab="dashboard"
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
        ),
        active_tab="logs"
    )

@rt("/admin/keys")
async def keys():
    repo = get_repository()
    all_keys = await repo.get_all_api_keys()
    
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
        ),
        active_tab="keys"
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
    repo = get_repository()
    keys = await repo.get_all_api_keys()
    current = next((k for k in keys if k.id == key_id), None)
    if current:
        await repo.update_api_key_status(key_id, not current.enabled)
    return ""
