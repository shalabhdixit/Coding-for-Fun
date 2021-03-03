package com.unitTest;

import static org.testng.Assert.assertEquals;

import org.testng.annotations.Test;

import com.sourceCode.StringUtil;

public class ReverseAnyString {

	@Test(testName = "Reverse String with valid characters", description = "Validate that string containing only valid characters should be reversed successfully", priority = 0)
	public void reverseString_ValidCharacters() {
		String str = "Sample string for unit testing";
		String actual = StringUtil.reverseString(str);
		String expected = "gnitset tinu rof gnirts elpmaS";

		// System.out.println(StringUtil.reverseString(str));
		assertEquals(actual, expected);
	}

	@Test(testName = "Reverse String with special characters", description = "Validate that string containing special characters should be reversed successfully", priority = 1)
	public void reverseString_SpecialCharacters() {
		String str = "$Sample @& string #$ for unit (testing)^";
		String actual = StringUtil.reverseString(str);
		String expected = "^)gnitset( tinu rof $# gnirts &@ elpmaS$";

		// System.out.println(StringUtil.reverseString(str));
		assertEquals(actual, expected);
	}

	@Test(testName = "Reverse Alphanumeric String", description = "Validate that alphanumeric string should be reversed successfully", priority = 2)
	public void reverseString_Alphanumeric() {
		String str = "1Sample 2string 3for 4unit 5testing6";
		String actual = StringUtil.reverseString(str);
		String expected = "6gnitset5 tinu4 rof3 gnirts2 elpmaS1";

		// System.out.println(StringUtil.reverseString(str));
		assertEquals(actual, expected);
	}

}