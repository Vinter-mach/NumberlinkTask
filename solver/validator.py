class InputValidator:

    @staticmethod
    def verified_pos_int(query_string, could_be_one):
        error_message = "Пожалуйста введите положительное число "
        if not could_be_one:
            error_message = error_message + "больше 1 "
        while True:
            print(query_string, end='')
            try:
                u_input = int(input())
                assert u_input > 0 and (could_be_one or u_input > 1)
                return u_input
            except AssertionError:
                print(error_message)
            except ValueError:
                print(error_message)
