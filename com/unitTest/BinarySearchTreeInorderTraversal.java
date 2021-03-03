package com.unitTest;


import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import com.sourceCode.Node;
import com.sourceCode.Tree;


class BinarySearchTreeInorderTraversal {
   Tree tree;
	Node treeRoot = null;
	
	/**
	 * Below is a sample Binary tree used
	 */
	//         100
	//		/		\
	//    40          150
	//	/	\		/	\
//	  20    60     120  180
	
	
	@BeforeMethod
	void setUp() throws Exception {
		tree = new Tree();
		Node element20 = new Node(20);
		Node element60 = new Node(60);
		Node element120 = new Node(120);
		Node element180 = new Node(180);
		Node element40 = new Node(element20,element60,40);
		Node element150 = new Node(element120,element180,150);
		Node element100 = new Node(element40,element150,100);
		treeRoot = element100;
	}

	@AfterMethod
	void tearDown() throws Exception {
		treeRoot = null;
	}

	@Test(testName="Inorder Traversal for Binary Search Tree", description="Validate that binary tree nodes should be displayed according to Inorder traversal")
	void BinarySearchTree_InorderTraveral() {
		tree.inorderTraveral(treeRoot);
	}

}
