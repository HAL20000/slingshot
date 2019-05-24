# -*- mode: python -*-

block_cipher = None


a = Analysis(['build/scripts-2.7/slingshot'],
             pathex=['build/lib.linux-x86_64-2.7/'],
             binaries=[],
             datas=[('build/lib.linux-x86_64-2.7/slingshot/data/', 'slingshot/data/'), ('build/scripts-2.7/slingshot', 'slingshot')],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='slingshot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='slingshot.ico')
