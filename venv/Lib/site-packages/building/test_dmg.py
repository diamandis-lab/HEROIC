from pathlib import Path
import subprocess
import re
import time, sys, os
import argparse
import shutil

thisFolder = Path(__file__).parent

with Path().home()/ 'keys/apple_ost_id' as p:
    IDENTITY = p.read_text().strip()
with Path().home()/ 'keys/apple_psychopy3_app_specific' as p:
    PWORD = p.read_text().strip()

ENTITLEMENTS = thisFolder / "entitlements.plist"
BUNDLE_ID = "org.opensciencetools.psychopy"
USERNAME = "admin@opensciencetools.org"

# handy resources for info:
#
# why use zip file to notarize as well as dmg:
#   https://deciphertools.com/blog/notarizing-dmg/
# notarize from Python:
#   https://github.com/najiji/notarizer/blob/master/notarize.py
# apple entitlements:
#     https://developer.apple.com/documentation/xcode/notarizing_macos_software_before_distribution/resolving_common_notarization_issues


class testDMG:
    def __init__(self, appFile, version, destination=None):
        self.appFile = Path(appFile)
        self.version = version
        self._dmgFile = None

    def dmgBuild(self):
        dmgFilename = str(self.appFile).replace(".app", "_rw.dmg")
        print(f"building dmg file: {dmgFilename}")
        # remove previous file if it's there
        if Path(dmgFilename).exists():
            os.remove(dmgFilename)
        # then build new one
        import dmgbuild
        icon = (thisFolder.parent /
                'psychopy/app/Resources/psychopy.icns').resolve()
        background = (thisFolder / "builtin-arrow.tiff").resolve()
        dmgbuild.build_dmg(
                filename=dmgFilename,
                volume_name=f'PsychoPy {self.version}',
                settings={
                    'format': 'UDRW',
                    'files': [str(thisFolder / 'dmg_settings.py')],
                    'symlinks': { 'Applications': '/Applications' },
                    'size': '3m', # but maybe irrelevant in UDRW mode?
                    'badge_icon': str(icon),
                    'background': None, #"builtin-arrow",
                    'icon_size': 128,
                    'icon_locations': {
                        'dmg_settings.py': (150, 160),
                        'Applications': (350, 160)
                    },
                    'window_rect': ((600, 600), (500, 400)),
                },
        )
        self._dmgFile = dmgFilename
        return dmgFilename

    def dmgCompress(self):
        dmgFinalFilename = str(self.appFile).replace(".app", f"_{self.version}.dmg")
        # remove previous file if it's there
        if Path(dmgFinalFilename).exists():
            os.remove(dmgFinalFilename)

        cmdStr = f"hdiutil convert {self._dmgFile} " \
                 f"-format UDZO " \
                 f"-o {dmgFinalFilename}"
        exitcode, output = subprocess.getstatusoutput(cmdStr)
        print(output)
        return dmgFinalFilename

def main():
        thistest = testDMG(appFile="psychoPy.app", version='20.2')
        thistest.dmgBuild()
        dmgFile = thistest.dmgCompress()


if __name__ == "__main__":
    main()
