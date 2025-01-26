<?php

	if (isset($_GET['page'])){
		
		$page = filter_var($_GET['page'], FILTER_SANITIZE_STRING);
		
		if ($page == "hurtownia_danych"){
			$component = file_get_contents("views/components/gcp_hurtownia_danych.html");
		}
		else if ($page == "opracowania_danych"){
			$component = file_get_contents("views/components/gcp_opracowania_danych.html");
		}
		else{
			$component = "404 - podstrona nie istnieje!";
		}
			
		
	}
	else{
		$component = file_get_contents("views/gcp_glowne_menu.html");
	}

	$header = file_get_contents("views/header.html");
	$footer = file_get_contents("views/footer.html");
	
	echo $header;
	echo $component;
	echo $footer;