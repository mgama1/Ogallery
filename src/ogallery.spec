# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['ogallery_main.py'],
             pathex=['/home/mgama1/ogallery_env/lib/python3.10/site-packages'],
             binaries=[],
             datas=[('config', 'config'),('core','core'),('custom.py','.'),('gallery','gallery'),('media','media'),('models','models')],
             hiddenimports=['pyzbar','cv2','numpy','pandas','Levenshtein',
                            'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
                            'PyQt5.sip',
                            'qtpy', 'qtawesome'],
             hookspath=[],
             hooksconfig={},
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
          name='ogallerydist',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ogallerydist')
