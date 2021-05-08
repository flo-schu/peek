# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    'six', 'comtypes','pythoncom','adodbapi','isapi'
]
hiddenimports += collect_submodules('nutrients')


block_cipher = None


a = Analysis(['src\\nutrient_timers.py'],
             pathex=[
                 'C:\\Users\\schunckf\\Documents\\Florian\\papers\\nanocosm\\src'
                 ],
             binaries=[],
             datas=[
                 ('C:\\Users\\schunckf\\Documents\\Florian\\papers\\nanocosm\\envs\\nutrients\\Lib\\site-packages\\beepy\\audio_data', 'beepy\\audio_data'),
                 ('C:\\Users\\schunckf\\Documents\\Florian\\papers\\nanocosm\\envs\\nutrients\\Lib\\site-packages\\pyttsx3', 'pyttsx3'),
                 ],
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='nutrispeech',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='nutrispeech')
