package api

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/anishtayin/agent/internal/core"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

type Server struct {
	httpServer *http.Server
	secretPath string
	xrayMgr    *core.XrayManager
}

func NewServer(secretPath string, xrayMgr *core.XrayManager) *Server {
	return &Server{
		secretPath: secretPath,
		xrayMgr:    xrayMgr,
	}
}

func (s *Server) Start(port string) error {
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Route(s.secretPath, func(r chi.Router) {
		r.Get("/health", s.handleHealth)
		r.Post("/api/users", s.handleAddUser)
		r.Delete("/api/users/{email}", s.handleRemoveUser)
	})

	r.NotFound(s.handleFake404)

	s.httpServer = &http.Server{Addr: ":" + port, Handler: r}
	log.Printf("Agent API listening on :%s", port)
	return s.httpServer.ListenAndServe()
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func (s *Server) handleAddUser(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Email      string `json:"email"`
		UUID       string `json:"uuid"`
		InboundTag string `json:"inbound_tag"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), 400)
		return
	}

	if s.xrayMgr == nil {
		http.Error(w, "Xray not available", 503)
		return
	}

	if err := s.xrayMgr.AddUser(r.Context(), req.InboundTag, req.Email, req.UUID); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}

	json.NewEncoder(w).Encode(map[string]bool{"success": true})
}

func (s *Server) handleRemoveUser(w http.ResponseWriter, r *http.Request) {
	email := chi.URLParam(r, "email")
	if s.xrayMgr == nil {
		http.Error(w, "Xray not available", 503)
		return
	}
	if err := s.xrayMgr.RemoveUser(r.Context(), "vless-reality", email); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	json.NewEncoder(w).Encode(map[string]bool{"removed": true})
}

func (s *Server) handleFake404(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusNotFound)
	w.Write([]byte("<html><body><h1>404 Not Found</h1></body></html>"))
}
