def pierwsza(n):
    return n * 2


def czwarta(f):
    def wewn(liczba):
        print("Jestem funkcja wewnetrzna")
        wynik = f(liczba)
        return wynik ** 2

    return wewn


f = czwarta(pierwsza)
