```python
import sympy as sp

def iki_bilinmeyenli_coz(a1, b1, c1, a2, b2, c2):
    x, y = sp.symbols('x y')
    denklem1 = a1 * x + b1 * y - c1
    denklem2 = a2 * x + b2 * y - c2
    cozum = sp.solve((denklem1, denklem2), (x, y))
    return cozum

# Örnek kullanım
sonuc = iki_bilinmeyenli_coz(1, 2, 3, 4, 5, 6)
print(sonuc)
```