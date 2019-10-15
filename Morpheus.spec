# -*- mode: python -*-

block_cipher = None


a = Analysis(['Morpheus.py'],
             pathex=['C:\\Users\\noepr\\Documents\\ECAM_5\\PRD EME\\Code\\Morpheus'],
             binaries=[],
             datas=[('eme.ico', '.'),
                    ('my_model.h5', '.'),
                    ('classes.json', '.'),
                    ('classes_entrainees.json', '.')],
             hiddenimports=[],
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
          name='Morpheus',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='eme.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Morpheus')
