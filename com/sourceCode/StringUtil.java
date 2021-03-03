/**
 * Defines set of reusable functions for an array
 * Function-1: getLength - It will give total length of String
 * Function-2: reverseString - It will return the reversed form of any Input String
 */

package com.sourceCode;

public class StringUtil {

	/**
	 * Function to retrieve length of the string
	 * 
	 * @param str
	 *            - Input parameter String for which length needs to be
	 *            calculated
	 * @return - length of input string as Integer value
	 */
	public static int getLength(String str) {
		/**
		 * Declaring string length variable - len, which has been initialized as
		 * 0 (ZERO) because it has to be looped through all the characters
		 * indexing from 0 (ZERO)
		 */
		int len;
		for (len = 0; 0 <= len; len++) {
			try {
				str.charAt(len);
			} catch (StringIndexOutOfBoundsException e) {
				break;
			}
		}
		return len;
	}

	/**
	 * Function to reverse the string
	 * 
	 * @param str
	 *            - Input parameter String which needs to be reversed
	 * @return - Reversed String as String value
	 */
	public static String reverseString(String str) {

		int length = getLength(str); // Retrieving length of input string
		String reversedString = "";

		for (int indx = length - 1; indx >= 0; indx--) {
			reversedString = reversedString + str.charAt(indx);
		}
		return reversedString;
	}
}
