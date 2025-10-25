import importlib
import logging
import pkgutil
import sys

import aiogram
from aiogram import Router



class RouterManager:
    def __init__(self, dp: aiogram.Dispatcher):
        self.dp: Router = dp

    def get_routers(self, package_name):
        routers = []
        package = importlib.import_module(package_name)

        for _, module_name, _ in pkgutil.walk_packages(package.__path__, package_name + "."):

            if module_name in sys.modules:
                module = sys.modules[module_name]
                # !!! ПЕРЕЗАГРУЖАЕМ МОДУЛЬ !!!
                importlib.reload(module)
            else:
                # Если модуль еще не был импортирован
                module = importlib.import_module(module_name)

            if hasattr(module, 'router'):
                routers.append(module.router)
        return routers

    def bind_routers(self, pkg_name):
        def import_submodules(package_name):
            """Динамический импорт всех модулей из указанного пакета."""
            package = importlib.import_module(package_name)
            for _, module_name, _ in pkgutil.walk_packages(package.__path__, package_name + "."):
                importlib.import_module(module_name)


        import_submodules(pkg_name)

        routers = self.get_routers(pkg_name)



        for router in routers:
            try:
                self.dp.sub_routers.append(router)
            except Exception as e:
                print(e)

    def unbind_routers(self):
        self.dp.sub_routers = []

    def apply_middleware(self1, cls):

        original_init = cls.__init__

        def new_init(self, *args, **kwargs):
            logging.info(f"Мидлвар {cls.__name__} инициализируется.")
            original_init(self, *args, **kwargs)
            try:
                self1.dp.message.middleware(self)
                self1.dp.callback_query.middleware(self)

                logging.info(f"Мидлвар {cls.__name__} привязан к диспатчеру.")
            except Exception as e:
                logging.error(e)


        cls.__init__ = new_init

        cls.was_decorated = True

        return cls

