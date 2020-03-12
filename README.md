# proyecto_is2

    Para escribir pruebas unitarias:

        La funcion ejemplo es la siguiente
        
            def dividir(a,b):
	            return a/b
	        
            Args:
                a (number): Dividendo
                b (numbers): divisor
         
            Retorna:
                El valor de la division (number)

    Se escribe una prueba de la siguiente manera:
    
        Se escribe una funcion con el prefijo "test_" y el nombre de la funcion
        Creamos una variable donde pondremos el valor de retorno de la funcion
        Por ultimo se hace una comparacion con assert
        
        def test_dividir():
	        resultado = dividir(15,3)
	        assert resultado == 5
	        
	    Se le pasa los argumentos que solicita la funcion
	    resultado: tendra el valor que devuelve la funcion dividir 
	    assert: compara el valor esperado que tendria que devolver la funcion, con el valor que 
	    devuelve la funcion.
	    Para este ejemplo el valor de retorno coincide con el valor esperado.
	    
	    
    Para correr pruebas unitarias:
        
        Se escribe el comando "pytest" dentro del proyecto y se analiza todos los archvos con el prefijo
        "test_" en ese directorio y empezara a correr nuestras pruebas
        Si no tiene el prefijo "test_" se tiene que poner despues de pytest el archivo donde se escribieron
        las pruebas, Ej: "pytest pruebas.py"