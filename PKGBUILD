pkgname="media-plyaer-controller"
pkgver=1.0
pkgrel=1
arch=('any')
pkgdesc="Small player for managing other music players"
url="https://github.com/4uf04eG/"
license=('GPL')
makedepends=('python-setuptools')
depends=('python' 'python-dbus')

package() {
    cd "$srcdir/${pkgname}-${pkgver}"
    python setup.py install --root="$pkgdir/" --optimize=1
}
