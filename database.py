from application import db


def init():
    import models
    db.create_all()


def populate_db():
    import models
    cat1 = models.Category('Bistro')
    cat2 = models.Category('Trattoria')
    cat3 = models.Category('Drive in restaurant')
    cat4 = models.Category('Drive thru restaurant')
    cat5 = models.Category('Pizzeria')
    cat6 = models.Category('Taverna')
    cat7 = models.Category('Cafe')
    cat8 = models.Category('Teahouse')
    cat9 = models.Category('Fast food')
    cat10 = models.Category('Tapas bar')
    cat11 = models.Category('Steakhouse')
    cat12 = models.Category('Food truck')

    db.session.add(cat1)
    db.session.add(cat2)
    db.session.add(cat3)
    db.session.add(cat4)
    db.session.add(cat5)
    db.session.add(cat6)
    db.session.add(cat7)
    db.session.add(cat8)
    db.session.add(cat9)
    db.session.add(cat10)
    db.session.add(cat11)
    db.session.add(cat12)

    db.session.commit()



