package message_generator

import (
	"encoding/json"
	"time"

	"github.com/domain-proxy/active_move_controller/api/active_mode"
	"github.com/domain-proxy/active_move_controller/api/requests"
)

func GenerateMessages(now clock, state *active_mode.State) []*requests.RequestPayload {
	var messages []message
	for _, config := range state.ActiveModeConfigs {
		generator := getPerCbsdMessageGenerator(now, config)
		messages = append(messages, generator.generateMessages(config)...)
	}
	payloads := make([]*requests.RequestPayload, len(messages))
	for i, m := range messages {
		payloads[i] = messageToRequest(m)
	}
	return payloads
}

type clock func() time.Time

func getPerCbsdMessageGenerator(now clock, config *active_mode.ActiveModeConfig) perCbsdMessageGenerator {
	if config.GetDesiredState() == active_mode.CbsdState_Unregistered {
		if config.GetCbsd().GetState() == active_mode.CbsdState_Registered {
			return &deregistrationMessageGenerator{}
		}
		return &noMessageGenerator{}
	}
	if config.GetCbsd().GetState() == active_mode.CbsdState_Unregistered {
		return &registerMessageGenerator{}
	}
	if len(config.GetCbsd().GetGrants()) != 0 {
		return &heartbeatMessageGenerator{now: now}
	}
	if len(config.GetCbsd().GetChannels()) != 0 {
		return &grantMessageGenerator{}
	}
	return &spectrumInquiryMessageGenerator{}
}

type perCbsdMessageGenerator interface {
	generateMessages(config *active_mode.ActiveModeConfig) []message
}

type message interface {
	name() string
}

func messageToRequest(m message) *requests.RequestPayload {
	data := map[string][]interface{}{
		m.name() + "Request": {m},
	}
	payload, _ := json.Marshal(data)
	return &requests.RequestPayload{Payload: string(payload)}
}

type noMessageGenerator struct{}

func (*noMessageGenerator) generateMessages(_ *active_mode.ActiveModeConfig) []message {
	return nil
}
