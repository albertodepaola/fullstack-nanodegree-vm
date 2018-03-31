
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

edit_form = ""
edit_form += "<html><body>"
edit_form += "<h1>Create new Restaurant!</h1>"
edit_form += '''<form method='POST' enctype='multipart/form-data' action='{}'><h2>What will the name be?</h2><input name="name" type="text" ><input type="submit" value="Submit"> </form>'''
edit_form += "</body></html>"

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>List of restaurans!</h1>"
                # output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += '''{}'''
                output += "</body></html>"
                restaurants = session.query(Restaurant).all()
                list_of_restaurants = ''
                for restaurant in restaurants:

                    list_of_restaurants += restaurant.__str__()
                    list_of_restaurants += "<br />"
                    list_of_restaurants += "<a href='/restaurants/{}/edit' >Edit</a>".format(restaurant.id)
                    list_of_restaurants += "<br />"
                    list_of_restaurants += "<a href='/restaurants/{}/delete' >Delete</a>".format(restaurant.id)
                    list_of_restaurants += "<br />"
                    list_of_restaurants += "<br />"

                output += "<a href='/restaurants/new'>Create Restaurant</a>"

                output = output.format(list_of_restaurants)
                self.wfile.write(output.encode())
                print(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = edit_form.format(self.path)
                self.wfile.write(output.encode())
                print(output)
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = edit_form.format(self.path)
                self.wfile.write(output.encode())

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')

                self.end_headers()
                try:
                    restaurant_id = self.path.split('/')[2]
                    r = session.query(Restaurant).filter_by(id=restaurant_id).one()
                    if r:
                        output = ""
                        output += "<html><body>"
                        output += "<h1>Are you sure you want to delete the restaurant??</h1>"
                        output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/{}/delete'><input type="submit" value="Submit"> </form>'''.format(restaurant_id)
                        output += "</body></html>"
                        self.wfile.write(output.encode())
                    else:
                        output = ""
                        output += "<html><body>"
                        output += "<h1>Restaurant not found</h1>"
                        output += "<a href='/restaurants'>Go back</a>"
                        output += "</body></html>"
                        self.wfile.write(output.encode())
                except:
                    self.send_response(303)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                    pass




            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = edit_form
                self.wfile.write(output.encode())
                print(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:

            print self.path
            if self.path.endswith("/hello"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                output = ""
                output += "<html><body>"
                output += " <h2> Okay, how about this: </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output.encode())
                print output

            if self.path.endswith("/restaurants/new"):
                print 'creating restaurant'
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                print ctype
                if ctype == 'multipart/form-data':
                    print('parsing fields')
                    fields = cgi.parse_multipart(self.rfile, pdict)

                    name = fields.get('name')

                    print(name[0])

                    new_restaurant = Restaurant(name=name[0])
                    session.add(new_restaurant)
                    session.commit()

            if self.path.endswith("/edit"):
                print("editing restaurant: " + self.path)
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                restaurant_id = self.path.split('/')[2]
                print("restaurant_id: " + restaurant_id)
                if ctype == 'multipart/form-data':
                    print('parsing fields')
                    fields = cgi.parse_multipart(self.rfile, pdict)

                    name = fields.get('name')

                    print(name[0])

                    edit_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                    edit_restaurant.name = name[0]
                    session.add(edit_restaurant)
                    session.commit()

            if self.path.endswith("/delete"):
                print("deleting restaurant: " + self.path)

                restaurant_id = self.path.split('/')[2]
                print("restaurant_id: " + restaurant_id)

                delete_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
                session.delete(delete_restaurant)
                session.commit()

            self.send_response(303)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

        except:
            print("Unexpected error:", sys.exc_info())
            raise


def main():
    try:
        port = 8081
        server = HTTPServer(('', port), webServerHandler)

        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()