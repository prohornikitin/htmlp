input-file.htmlp

.. code:: html

	<!DOCTYPE html>
	<html>
		<def tag="red-text">
			<span style="color: red">$children</span>
		</def>
	    <red-text>Hello world</red-text>
	</html>

output.html

.. code:: html

	<!DOCTYPE html>
	<html>
	    <span style="color: red">Hello world</span>
	</html>