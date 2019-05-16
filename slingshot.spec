# -*- mode: python -*-

block_cipher = None


a = Analysis(['/usr/bin/slingshot'],
             pathex=['build/lib/', 'Z:\\home\\hal\\slingshot'],
             binaries=[],
             datas=[('build/lib/slingshot/data/', 'slingshot/data/'), ('build/scripts-2.7/slingshot', 'slingshot')],
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
