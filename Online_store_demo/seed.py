from models import *
from app import app

db.drop_all()
db.create_all()

'''username, location, address, password , email, image_url'''

User.signup('Kolobok_admin', 'USA', '1 main street, Boston, MA', 'qwe123', 'kolobok@snacks.com')
User.signup('BobHope69', 'Canada', 'addressInCanada', 'qwe123', 'bobCanada@snacks.com')
User.signup('illushahuivoshi', 'Mexico', 'addressInMexico', 'qwe123', 'illMexico@snacks.com')


'''name, category, weight, description , price, quantity, image_url'''

Product.add('Bread loaf', 'Bread', '250', 'Bread is bread', 3.25, 5, 'https://omgitsglutenfree.com/wp-content/uploads/2018/05/5-grain-bread.jpg')
Product.add('Ogurchik', 'Katanki', '600', 'Salty cucumbers', 5.89, 11, 'https://www.vlasic.com/sites/g/files/qyyrlu671/files/images/products/original-dill-wholes-40069.png')
Product.add('Kartoffel', 'Vegetables', '1000', ' Potato, but in German', 4.73, 21, 'https://www.hagengrote.de/genussmagazin/wp-content/uploads/2017/09/Fotolia_100278924_XL-1024x768.jpg')