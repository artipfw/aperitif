package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

func main() {
	// apiKey := os.Getenv("OPENAI_API_KEY")
	// if apiKey == "" {
	apiKey := "fake"
	// }

	client := openai.NewClient(
		option.WithAPIKey(apiKey),
		option.WithBaseURL("https://phi-4-multimodal-instruct-guillaume-derouville-7ea5e77d.koyeb.app/v1"),
	)

	ctx := context.Background()

	chatCompletion, err := client.Chat.Completions.New(ctx, openai.ChatCompletionNewParams{
		Messages: []openai.ChatCompletionMessageParamUnion{
			openai.UserMessage("Tell me a joke."),
		},
		Model:     "microsoft/phi-4",
		MaxTokens: openai.Int(30),
	})
	if err != nil {
		log.Fatal(err)
	}

	jsonOutput, err := json.MarshalIndent(chatCompletion, "", "    ")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(jsonOutput))
}
