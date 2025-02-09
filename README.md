# swinip

**swinip** — это скрипт для обновления списков точечной блокировки для протоколов WireGuard и AmneziaWG на прошивке OpenWRT. Он автоматически обновляет файл сетевых настроек `/etc/config/network` раз в сутки (или с выбранной вами частотой). Списки IP-адресов для блокировки заполняются вручную и хранятся в репозитории на GitHub. Основное назначение скрипта — поддержка актуального списка IP-адресов сайтов, которые блокируются по IP или ограничивают доступ для пользователей из России. Важно отметить, что большая часть блокировок обходится через сокрытие DPI, поэтому список небольшой.

## Требования

- Уже настроенный сетевой интерфейс WireGuard или AmneziaWG.
- Достаточно места для установки Python.

## Установка

1. Обновите списки пакетов, установите Python и поддержку виртуальных окружений:

    ```sh
    opkg update
    opkg install python3
    opkg install python3-venv
    ```

2. Клонируйте репозиторий на свой роутер:

    ```sh
    git clone https://github.com/Alvel007/swinip.git
    ```

3. Перейдите в папку `swinip`, создайте виртуальное окружение и активируйте его:

    ```sh
    cd swinip
    python3 -m venv myenv
    source myenv/bin/activate
    ```

4. Установите все зависимости из `requirements.txt`:

    ```sh
    pip install -r requirements.txt
    ```

## Настройка

1. Откройте скрипт в любом текстовом редакторе и настройте следующие переменные:
    - `url` — ссылка на файл со списками IP ресурсов, которые будут использоваться через VPN. Вы можете создать свои списки и заменить ссылку.
    - `wg_name` — наименование сетевого интерфейса WireGuard/AmneziaWG.
    - `wg_interface_name` — наименование расширенных настроек интерфейса WireGuard/AmneziaWG.

2. Настройка cron для автоматического запуска скрипта:

    - Проверьте статус cron:

        ```sh
        /etc/init.d/cron status
        ```

    - Если cron не запущен, активируйте его:

        ```sh
        /etc/init.d/cron enable
        /etc/init.d/cron start
        ```

    - Откройте файл настроек cron для редактирования:

        ```sh
        EDITOR=nano crontab -e
        ```

    - Добавьте следующую строку для запуска скрипта ежедневно в 5 утра:

        ```sh
        0 5 * * * /fire/swinip/myenv/bin/python /fire/swinip/doip.py >> /fire/swinip/cronjob.log 2>&1
        ```

    - Перезапустите cron:

        ```sh
        /etc/init.d/cron restart
        ```

## Отладка

Вы можете вручную выполнить скрипт, чтобы проверить правильность его работы:

```sh
/fire/swinip/myenv/bin/python /fire/swinip/doip.py
```
Это эмулирует выполнение скрипта через cron и позволяет убедиться, что все пути и виртуальное окружение настроены верно.

## О скрипте
Этот скрипт был разработан для автоматизации управления несколькими роутерами, которые я настраивал для своих друзей. Он помогает автоматически обновлять точечные списки обхода блокировки для протоколов WireGuard и AmneziaWG, учитывая настройку сокрытия DPI, и не перегружает память роутера списками на тысячи IP-адресов, внесённых в реестр РКН. Скрипт написан быстро, так что прошу не судить строго за код.