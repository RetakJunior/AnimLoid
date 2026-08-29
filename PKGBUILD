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
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("https://files.pythonhosted.org/packages/source/a/animloid/animloid-$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
}