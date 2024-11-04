from django.db import models


class RangeLookup(models.Lookup):
    lookup_name = 'range'

    def get_prep_lookup(self):
        if not isinstance(self.rhs, tuple) or len(self.rhs) != 2 or not all(isinstance(i, int) for i in self.rhs):
            raise ValueError("The 'range' lookup requires a tuple with exactly two elements.")
        return self.rhs

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        value, range_value = rhs_params[0]
        range_value /= 2
        lower_bound = value - range_value
        upper_bound = value + range_value

        sql = f"{lhs} BETWEEN %s AND %s"
        params = [lower_bound, upper_bound]

        return sql, params


models.IntegerField.register_lookup(RangeLookup)
