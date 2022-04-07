# -*- mode: python ; coding: utf-8 -*-
from kivy.tools.packaging import pyinstaller_hooks as hooks
from kivy_deps import sdl2, glew
from kivy import kivy_data_dir
from os.path import join
block_cipher = None
kivy_deps_all = hooks.get_deps_all()
kivy_factory_modules = hooks.get_factory_modules()

# list of hiddenimports
hiddenimports = kivy_deps_all['hiddenimports'] + kivy_factory_modules + ['win32timezone', 'solar_gui.resources']

# binary data
sdl2_bin_tocs = [Tree(p) for p in sdl2.dep_bins]
glew_bin_tocs = [Tree(p) for p in glew.dep_bins]
bin_tocs = sdl2_bin_tocs + glew_bin_tocs

# list of modules to exclude from analysis
#excludes_a = ['Tkinter', '_tkinter', 'twisted', 'docutils', 'pygments']

# assets
kivy_assets_toc = Tree(kivy_data_dir, prefix=join('kivy_install', 'data'))
assets_toc = [kivy_assets_toc]
tocs = bin_tocs + assets_toc

datas = [
    ('src\\solar_gui\\core\\main.kv','solar_gui\\core'),
    ('src\\solar_gui\\resources\\orion-nebula.jpg','solar_gui\\resources')
]

a = Analysis(['src\\solar_gui\\__main__.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=hooks.hookspath(),
             runtime_hooks=hooks.runtime_hooks(),
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher
             )

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *tocs,
          debug=False,
          strip=False,
          upx=True,
          console=False,
          name='solar',
          runtime_tmpdir=None,
          uac_admin=True )
