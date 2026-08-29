# PKGBUILD
pkgname=animloid
pkgver=2.7.0
pkgrel=1
pkgdesc="CLI tabanlı anime izleme ve indirme aracı"
arch=('any')
url="https://github.com/RetakJunior/AnimLoid"
license=('CC-BY-NC-ND-4.0')
depends=(
    'python'
    'python-typer'
    'python-rich'
    'python-questionary'
    'python-requests'
    'python-packaging'
    'python-beautifulsoup4'
    'python-lxml'
    'python-pycryptodome'
    'python-appdirs'
    'python-prompt_toolkit'
    'python-pyfiglet'
    'python-py7zr'
)
makedepends=('git' 'python-build' 'python-installer' 'python-wheel' 'python-setuptools')
provides=('animloid')
conflicts=('animloid')
source=("git+https://github.com/RetakJunior/AnimLoid.git")
sha256sums=('SKIP')

pkgver() {
  cd AnimLoid
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

build() {
  cd AnimLoid
  python -m build --wheel --no-isolation
}

package() {
  cd AnimLoid
  python -m installer --destdir="$pkgdir" dist/*.whl
}