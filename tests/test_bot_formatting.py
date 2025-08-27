from src.bot.bot import format_car

def test_format_car():
    car = {'id': 1, 'name': 'Model 3', 'price': 39999, 'brand_id': 2}
    text = format_car(car)
    assert '#1' in text and 'Model 3' in text and '39999' in text
