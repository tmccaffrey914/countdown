import cherrypy
import play


class Root(object):
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def consonant(self):
        return {"consonant": play.get_consonant()}

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def vowel(self):
        return {"vowel": play.get_vowel()}


if __name__ == '__main__':
    cherrypy.quickstart(Root(), '/')
