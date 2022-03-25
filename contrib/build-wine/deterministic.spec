# -*- mode: python -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs


for i, x in enumerate(sys.argv):
    if x == '--name':
        cmdline_name = sys.argv[i+1]
        break
else:
    raise Exception('no name')

hiddenimports = []
hiddenimports += collect_submodules('pkg_resources')  # workaround for https://github.com/pypa/setuptools/issues/1963
hiddenimports += collect_submodules('trezorlib')
hiddenimports += collect_submodules('safetlib')
hiddenimports += collect_submodules('btchip')
hiddenimports += collect_submodules('keepkeylib')
hiddenimports += collect_submodules('websocket')

# safetlib imports PyQt5.Qt.  We use a local updated copy of pinmatrix.py until they
# release a new version that includes https://github.com/archos-safe-t/python-safet/commit/b1eab3dba4c04fdfc1fcf17b66662c28c5f2380e
hiddenimports.remove('safetlib.qt.pinmatrix')

hiddenimports += [
    'electrum_zcash',
    'electrum_zcash.base_crash_reporter',
    'electrum_zcash.base_wizard',
    'electrum_zcash.plot',
    'electrum_zcash.qrscanner',
    'electrum_zcash.websockets',
    'electrum_zcash.gui.qt',
    'PyQt5.sip',
    'PyQt5.QtPrintSupport',  # needed by Revealer

    'electrum_zcash.plugins',

    'electrum_zcash.plugins.hw_wallet.qt',

    'electrum_zcash.plugins.audio_modem.qt',
    'electrum_zcash.plugins.cosigner_pool.qt',
    'electrum_zcash.plugins.digitalbitbox.qt',
    'electrum_zcash.plugins.email_requests.qt',
    'electrum_zcash.plugins.keepkey.qt',
    'electrum_zcash.plugins.revealer.qt',
    'electrum_zcash.plugins.labels.qt',
    'electrum_zcash.plugins.scan_over_gap.qt',
    'electrum_zcash.plugins.trezor.qt',
    'electrum_zcash.plugins.safe_t.client',
    'electrum_zcash.plugins.safe_t.qt',
    'electrum_zcash.plugins.ledger.qt',
    'electrum_zcash.plugins.virtualkeyboard.qt',
]

datas = [
#    ('electrum_zcash/checkpoints*.*', 'electrum_zcash'),
    ('electrum_zcash/*.json', 'electrum_zcash'),
    ('electrum_zcash/locale', 'electrum_zcash/locale'),
    ('electrum_zcash/wordlist', 'electrum_zcash/wordlist'),
    ('electrum_zcash/gui/icons', 'electrum_zcash/gui/icons'),
    ('C:\\zbarw', '.'),
]

datas += collect_data_files('trezorlib')
datas += collect_data_files('safetlib')
datas += collect_data_files('btchip')
datas += collect_data_files('keepkeylib')

binaries = []
# Add libusb so Trezor and Safe-T mini will work
binaries += [('C:/Python38/libusb-1.0.dll', '.')]
binaries += [('C:/x11_hash/libx11hash-0.dll', '.')]
binaries += [('C:/libsecp256k1/libsecp256k1-0.dll', '.')]
binaries += [('C:/zbarw/libzbar-0.dll', '.')]

# Workaround for "Retro Look":
binaries += [b for b in collect_dynamic_libs('PyQt5') if 'qwindowsvista' in b[0]]

# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-remove-tkinter-tcl
sys.modules['FixTk'] = None
excludes = ['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter']
excludes += [
    'PyQt5.QtBluetooth',
    'PyQt5.QtCLucene',
    'PyQt5.QtDBus',
    'PyQt5.Qt5CLucene',
    'PyQt5.QtDesigner',
    'PyQt5.QtDesignerComponents',
    'PyQt5.QtHelp',
    'PyQt5.QtLocation',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaQuick_p',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtNetworkAuth',
    'PyQt5.QtNfc',
    'PyQt5.QtOpenGL',
    'PyQt5.QtPositioning',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickParticles',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtSql',
    'PyQt5.Qt5Sql',
    'PyQt5.Qt5Svg',
    'PyQt5.QtTest',
    'PyQt5.QtWebChannel',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebKit',
    'PyQt5.QtWebKitWidgets',
    'PyQt5.QtWebSockets',
    'PyQt5.QtXml',
    'PyQt5.QtXmlPatterns',
    'PyQt5.QtWebProcess',
    'PyQt5.QtWinExtras',
]

a = Analysis(['electrum-zcash'],
             hiddenimports=hiddenimports,
             datas=datas,
             binaries=binaries,
             excludes=excludes,
             runtime_hooks=['pyi_runtimehook.py'])

# http://stackoverflow.com/questions/19055089/
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

# Strip out parts of Qt that we never use. Reduces binary size by tens of MBs. see #4815
qt_bins2remove=('qt5web', 'qt53d', 'qt5game', 'qt5designer', 'qt5quick',
                'qt5location', 'qt5test', 'qt5xml', r'pyqt5\qt\qml\qtquick')
print("Removing Qt binaries:", *qt_bins2remove)
for x in a.binaries.copy():
    for r in qt_bins2remove:
        if x[0].lower().startswith(r):
            a.binaries.remove(x)
            print('----> Removed x =', x)

qt_data2remove=(r'pyqt5\qt\translations\qtwebengine_locales', )
print("Removing Qt datas:", *qt_data2remove)
for x in a.datas.copy():
    for r in qt_data2remove:
        if x[0].lower().startswith(r):
            a.datas.remove(x)
            print('----> Removed x =', x)

# hotfix for #3171 (pre-Win10 binaries)
a.binaries = [x for x in a.binaries if not x[1].lower().startswith(r'c:\windows')]

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          debug=False,
          strip=False,
          upx=False,
          console=False,
          icon='electrum_zcash/gui/icons/electrum-zcash.ico',
          name=os.path.join('build\\pyi.win32\\electrum', cmdline_name))

# exe with console output
conexe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          debug=False,
          strip=False,
          upx=False,
          console=True,
          icon='electrum_zcash/gui/icons/electrum-zcash.ico',
          name=os.path.join('build\\pyi.win32\\electrum',
                            'console-%s' % cmdline_name))

coll = COLLECT(exe, conexe,
               a.binaries,
               a.datas,
               strip=False,
               upx=False,
               name=os.path.join('dist', 'electrum-zcash'))
