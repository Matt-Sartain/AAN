jQuery.fn.dataTableExt.aTypes.unshift(
	function ( sData )
	{
		var sValidChars = "0123456789-,";
		var Char;
		var bDecimal = false;
		
		/* Check the numeric part */
		for ( i=0 ; i<sData.length ; i++ )
		{
			Char = sData.charAt(i);
			if (sValidChars.indexOf(Char) == -1)
			{
				return null;
			}
			
			/* Only allowed one decimal place... */
			//if ( Char == "," )
			//{
			//	if ( bDecimal )
			//	{
			//		return null;
			//	}
			//	bDecimal = true;
			//}
		}
		
		return 'numeric-comma';
	}
);