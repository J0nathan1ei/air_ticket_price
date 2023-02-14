package main

import "github.com/gin-gonic/gin"

func main() {
	router := gin.Default() // get gin engine
	router.GET("/hello", func(c *gin.Context) {
		c.JSON(200, gin.H{ // response json
			"message": "hello world",
		})
	})
	_ = router.RunTLS(":443", "./server.crt", "./server.key")
}