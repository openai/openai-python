#!/bin/bash
# openai CLI Shell Completion
# Generated for issue #843: Add shell auto completion

_openai_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="api_base api_key api_type azure_ad_token azure_endpoint help organization proxy verbose version"

    case "${prev}" in
        -b|--api-base|-k|--api-key|-o|--organization|-p|--proxy|-t|--api-type|--api-version|--azure-endpoint|--azure-ad-token)
            return 0
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

complete -F _openai_complete openai
