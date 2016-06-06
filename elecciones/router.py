class VoteRouter(object):

    def db_for_read(self, model, **hints):
        return 'vote_db'

    def db_for_write(self, model, **hints):
        return 'vote_db'

    def allow_relation(self, obj1, obj2, **hints):
        return 'vote_db'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return 'vote_db'