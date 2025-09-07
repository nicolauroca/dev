#!/usr/bin/env python3
import os, re, sys, argparse, datetime, zipfile, pathlib

def slugify(name: str) -> str:
    s = name.strip()
    s = re.sub(r'^com_', '', s, flags=re.I)  # remove com_ prefix if provided
    s = re.sub(r'[^a-zA-Z0-9]+', '_', s)
    s = s.strip('_').lower()
    return s or 'component'

def pascal_case(s: str) -> str:
    parts = re.split(r'[^a-zA-Z0-9]', s)
    return ''.join(p.capitalize() for p in parts if p)

def human_title(s: str) -> str:
    s = re.sub(r'[_\-]+', ' ', s.strip())
    s = re.sub(r'\s+', ' ', s)
    return s.title() if s else 'Component'

def render(template: str, mapping: dict) -> str:
    # Simple token replacement using __TOKEN__ markers to avoid brace conflicts
    out = template
    for k, v in mapping.items():
        out = out.replace(f"__{k}__", v)
    return out

TEMPLATE = {
"manifest": """<?xml version="1.0" encoding="utf-8"?>
<extension type="component" method="upgrade">
  <name>com___SLUG__</name>
  <creationDate>__DATE__</creationDate>
  <author>__AUTHOR__</author>
  <version>__VERSION__</version>
  <description>__TITLE__ para Joomla 5 (admin) — scaffold autogenerado</description>

  <!-- Namespace PSR-4 base para el componente -->
  <namespace path="src">__VENDOR__\\Component\\__PASCAL__</namespace>

  <administration>
    <menu>__MENU__</menu>
    <files folder="admin">
      <folder>services</folder>
      <folder>src</folder>
      <folder>tmpl</folder>
    </files>
  </administration>
</extension>
""",
"provider": r"""<?php
defined('_JEXEC') or die;

use Joomla\DI\Container;
use Joomla\DI\ServiceProviderInterface;

use Joomla\CMS\Extension\ComponentInterface;
use Joomla\CMS\Dispatcher\ComponentDispatcherFactoryInterface;
use Joomla\CMS\MVC\Factory\MVCFactoryInterface;

use Joomla\CMS\Extension\Service\Provider\ComponentDispatcherFactory;
use Joomla\CMS\Extension\Service\Provider\MVCFactory;

use __VENDOR__\Component\__PASCAL__\Administrator\Extension\__PASCAL__Component;

return new class implements ServiceProviderInterface
{
    public function register(Container $container): void
    {
        $namespace = '\\__VENDOR__\\Component\\__PASCAL__';

        $container->registerServiceProvider(new ComponentDispatcherFactory($namespace));
        $container->registerServiceProvider(new MVCFactory($namespace));

        $container->set(
            ComponentInterface::class,
            function (Container $container) {
                $component = new __PASCAL__Component(
                    $container->get(ComponentDispatcherFactoryInterface::class)
                );
                $component->setMVCFactory($container->get(MVCFactoryInterface::class));
                return $component;
            }
        );
    }
};
""",
"extension_class": r"""<?php
namespace __VENDOR__\Component\__PASCAL__\Administrator\Extension;

defined('_JEXEC') or die;

use Joomla\CMS\Extension\MVCComponent;

class __PASCAL__Component extends MVCComponent
{
}
""",
"display_controller": r"""<?php
namespace __VENDOR__\Component\__PASCAL__\Administrator\Controller;

defined('_JEXEC') or die;

use Joomla\CMS\MVC\Controller\BaseController;

class DisplayController extends BaseController
{
    protected $default_view = '__VIEW__';
}
""",
"html_view": r"""<?php
namespace __VENDOR__\Component\__PASCAL__\Administrator\View\__VIEWPASCAL__;

defined('_JEXEC') or die;

use Joomla\CMS\MVC\View\HtmlView as BaseHtmlView;

class HtmlView extends BaseHtmlView
{
    public string $greeting = 'Hello, World! 👋';

    public function display($tpl = null)
    {
        return parent::display($tpl);
    }
}
""",
"layout_default": r"""<?php
defined('_JEXEC') or die;
?>
<div class="container">
    <h1>__MENU__ (Admin)</h1>
    <p><?php echo $this->greeting; ?></p>
    <p>Este es el scaffold básico. Actualiza este layout a tu gusto.</p>
</div>
""",
"readme": """# __TITLE__ (Admin) — Joomla 5 Component Scaffold

Estructura generada automáticamente.

## Estructura
- admin/services/provider.php — Service Provider (inyecta Extension, Dispatcher y MVCFactory)
- admin/src/Extension/__PASCAL__Component.php — Clase Extension (extiende MVCComponent)
- admin/src/Controller/DisplayController.php — Controlador por defecto (vista __VIEW__)
- admin/src/View/__VIEWPASCAL__/HtmlView.php — Vista __VIEW__
- admin/tmpl/__VIEW__/default.php — Layout de la vista

## Manifest
- __MANIFEST__ con:
  - <name>com___SLUG__</name>
  - <namespace path="src">__VENDOR__\\Component\\__PASCAL__</namespace>
  - <menu>__MENU__</menu>

## Notas PSR-4
- El segmento 'Administrator' está en el **namespace**, no en la ruta: Joomla mapea
  - __VENDOR__\\Component\\__PASCAL__\\Administrator\\* → administrator/components/com___SLUG__/src/*
  - __VENDOR__\\Component\\__PASCAL__\\Site\\* → components/com___SLUG__/src/*

## Instalación
1) Comprime la carpeta `com___SLUG__` en zip o usa el zip generado (si eliges --zip).
2) Instala en Joomla: System → Extensions → Install.
3) Ve a Components → __MENU__.
"""
}

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def build_scaffold(target_root, slug, vendor, title, menu, author, version, view, do_zip):
    Pascal = pascal_case(slug)
    ViewPascal = pascal_case(view)
    date = datetime.date.today().isoformat()
    pkg_dir = os.path.join(target_root, f"com_{slug}")
    manifest_name = f"{slug}.xml"

    m = {
        "SLUG": slug,
        "DATE": date,
        "AUTHOR": author,
        "VERSION": version,
        "TITLE": title,
        "VENDOR": vendor,
        "PASCAL": Pascal,
        "MENU": menu,
        "VIEW": view,
        "VIEWPASCAL": ViewPascal,
        "MANIFEST": manifest_name,
    }

    files = {
        os.path.join(pkg_dir, manifest_name): render(TEMPLATE["manifest"], m),
        os.path.join(pkg_dir, "admin", "services", "provider.php"): render(TEMPLATE["provider"], m),
        os.path.join(pkg_dir, "admin", "src", "Extension", f"{Pascal}Component.php"): render(TEMPLATE["extension_class"], m),
        os.path.join(pkg_dir, "admin", "src", "Controller", "DisplayController.php"): render(TEMPLATE["display_controller"], m),
        os.path.join(pkg_dir, "admin", "src", "View", ViewPascal, "HtmlView.php"): render(TEMPLATE["html_view"], m),
        os.path.join(pkg_dir, "admin", "tmpl", view, "default.php"): render(TEMPLATE["layout_default"], m),
        os.path.join(pkg_dir, "README.md"): render(TEMPLATE["readme"], m),
    }

    for path, content in files.items():
        write_file(path, content)

    zip_path = None
    if do_zip:
        zip_path = os.path.join(target_root, f"com_{slug}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, filenames in os.walk(pkg_dir):
                for name in filenames:
                    full = os.path.join(root, name)
                    rel = os.path.relpath(full, os.path.dirname(pkg_dir))
                    z.write(full, rel)
    return pkg_dir, zip_path

def main():
    ap = argparse.ArgumentParser(description="Genera un componente básico de administración para Joomla 5 (MVC, PSR-4, provider)")
    ap.add_argument("--name", required=True, help="Nombre del componente (con o sin 'com_'), ej: helloadminworld")
    ap.add_argument("--path", required=True, help="Ruta destino donde crear la carpeta com_<name>")
    ap.add_argument("--vendor", default="Nico", help="Vendor/raíz del namespace PSR-4 (por defecto: Nico)")
    ap.add_argument("--menu", default=None, help="Etiqueta a mostrar en Components (por defecto: Title Case del name)")
    ap.add_argument("--title", default=None, help="Título/Descripción humana (por defecto: menu)")
    ap.add_argument("--author", default="Nico", help="Autor para el manifest")
    ap.add_argument("--version", default="1.0.0", help="Versión del componente")
    ap.add_argument("--view", default="hello", help="Nombre de la vista por defecto (y carpeta tmpl)")
    ap.add_argument("--zip", action="store_true", help="Generar también un ZIP instalable")
    args = ap.parse_args()

    slug = slugify(args.name)
    vendor = args.vendor.strip().replace('/', '\\')
    menu = args.menu if args.menu else human_title(slug)
    title = args.title if args.title else menu
    target_root = os.path.abspath(args.path)

    pkg_dir, zip_path = build_scaffold(
        target_root=target_root,
        slug=slug,
        vendor=vendor,
        title=title,
        menu=menu,
        author=args.author,
        version=args.version,
        view=args.view,
        do_zip=args.zip,
    )

    print("Carpeta generada:", pkg_dir)
    if zip_path:
        print("ZIP instalable:", zip_path)

if __name__ == "__main__":
    main()
