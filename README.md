# KTGUtils: Dynamic Router & Middleware Manager for Aiogram

KTGUtils is a lightweight utility package designed to significantly enhance router management and development efficiency within Aiogram (v3+)-based Telegram bots. It provides an elegant solution for automatically discovering, loading, and refreshing your bot's routing logic.

## 🌟 Key Features

* **Dynamic Router Discovery:** Automatically scans a specified package (folder) to find all `Router` instances defined in separate modules.
* **Hot Reloading Support:** Unlike standard Python imports, this manager can **explicitly reload** router modules at runtime. This is invaluable for development, allowing you to quickly test changes to handlers or filters without restarting the entire bot.
* **Automated Middleware Binding:** Simplifies the complex process of attaching your custom Middleware classes to the dispatcher's handlers.

## 📦 Installation

Since your package is likely called `ktgutils` on PyPI:

```bash
pip install ktgutils
````

## 🚀 Usage

### 1\. Router Management

Define your routers as usual in separate files (e.g., `handlers/user_commands.py`, `handlers/admin.py`).

```python
# main.py

from aiogram import Dispatcher
from ktgutils import RouterManager

# Initialize Dispatcher
dp = Dispatcher()

# Initialize Router Manager
router_manager = RouterManager(dp=dp)

# Bind all routers found inside the 'handlers' package
router_manager.bind_routers("handlers")

# --- Development Use Case (Hot Reloading) ---
# If you make changes to a handler file (e.g., handlers/user_commands.py)
# while the bot is running, simply call this again to refresh the logic:
# router_manager.bind_routers("handlers") 
# (Note: bind_routers automatically clears and reloads/rebinds)

# To manually clear all bound routers:
# router_manager.unbind_routers()
```

### 2\. Automated Middleware Application

Applying the same Middleware to both message handlers and callback queries can be repetitive. Use the `@RouterManager.apply_middleware` decorator to handle this automatically when the Middleware class is instantiated.

```python
# middleware/user_check.py

from ktgutils import RouterManager
from aiogram.types import Message, CallbackQuery

# Note: The decorator MUST be applied via the RouterManager instance/class
@RouterManager.apply_middleware
class UserCheckMiddleware:
    def __init__(self, user_role: str):
        # This original __init__ is called first
        self.role = user_role

    async def __call__(self, handler, event: Message | CallbackQuery, data: dict):
        # Your actual middleware logic
        # For example:
        # if data.get('user_role') != self.role:
        #     return # Block the handler

        return await handler(event, data)

# --- In your main bot setup ---

# Instantiate the Middleware class. The decorator handles binding to the dispatcher.
user_middleware = UserCheckMiddleware(user_role="admin")
```

## ⚙️ How It Works

The core functionality is provided by the `get_routers` method, which uses Python's built-in **`pkgutil.walk_packages`** to recursively scan the specified directory. It then uses **`importlib.reload(module)`** to bypass the standard Python module cache (`sys.modules`) and load the latest version of the module from the disk, ensuring that all defined `router` objects are up-to-date before being bound to the Dispatcher.
