# for use with python dmgbuild

# thisFolder = Path(__file__).parent

format = 'UDRW'
size = '2g'
files = ['../dist/PsychoPy.app']
# files = ['updateBuilderDemos.py']
symlinks = { 'Applications': '/Applications' }
# size = '20'
badge_icon = '/Users/lpzjwp/code/psychopy/git/psychopy/app/Resources/psychopy.icns'
icon_locations = {
    'PsychoPy.app': (200, 190),
    'Applications': (440, 190)
}
window_rect = ((600, 600), (640, 400))
default_view = 'icon_view'
background = '/Users/lpzjwp/code/psychopy/git/building/builtin-arrow.png'
icon_size = 128
text_size = 36
