"""
SOP Data Loader Utility

Provides functionality to load Standard Operating Procedures (SOPs) from markdown files
stored in either local file system or S3 storage. Includes metadata parsing, caching,
and search capabilities.
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class SOPDataLoader:
    """
    Utility class for loading and managing SOP documents from markdown files.
    
    Supports both local file system and S3 storage modes with automatic fallback.
    Provides caching, metadata parsing, and search functionality.
    """
    
    def __init__(self, use_s3: bool = False, base_path: str = None, s3_bucket: str = None, s3_prefix: str = "sop/"):
        """
        Initialize SOP data loader.
        
        Args:
            use_s3: Whether to use S3 storage instead of local files
            base_path: Base path for local file storage (defaults to project sop directory)
            s3_bucket: S3 bucket name (defaults to config value)
            s3_prefix: S3 key prefix for SOP files
        """
        self.use_s3 = use_s3
        self.s3_bucket = s3_bucket or os.getenv("S3_BUCKET_NAME", "manufacturing-systems-data")
        self.s3_prefix = s3_prefix
        
        # Set up local base path
        if base_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            base_path = os.path.join(project_root, "manufacturing-data", "sop")
        
        self.base_path = base_path
        
        # Initialize caches
        self._sop_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 3600  # 1 hour cache TTL
        
        # Initialize S3 client if needed
        self._s3_client = None
        if self.use_s3:
            self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client with proper error handling."""
        try:
            # Try to use configured AWS profile if available
            aws_profile = os.getenv("AWS_PROFILE")
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
                self._s3_client = session.client('s3')
            else:
                self._s3_client = boto3.client('s3', region_name=aws_region)
            
            # Test S3 connectivity
            self._s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"S3 client initialized successfully for bucket: {self.s3_bucket}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Falling back to local storage.")
            self.use_s3 = False
            self._s3_client = None
        except ClientError as e:
            logger.error(f"S3 bucket access error: {e}. Falling back to local storage.")
            self.use_s3 = False
            self._s3_client = None
        except Exception as e:
            logger.error(f"Unexpected S3 initialization error: {e}. Falling back to local storage.")
            self.use_s3 = False
            self._s3_client = None
    
    def _is_cache_valid(self) -> bool:
        """Check if the current cache is still valid based on TTL."""
        if self._cache_timestamp is None:
            return False
        
        elapsed = (datetime.now() - self._cache_timestamp).total_seconds()
        return elapsed < self._cache_ttl_seconds
    
    def _list_sop_files(self) -> List[str]:
        """
        List all SOP markdown files from storage.
        
        Returns:
            List of SOP filenames
        """
        if self.use_s3 and self._s3_client:
            return self._list_s3_files()
        else:
            return self._list_local_files()
    
    def _list_local_files(self) -> List[str]:
        """List SOP files from local file system."""
        try:
            if not os.path.exists(self.base_path):
                logger.warning(f"SOP directory does not exist: {self.base_path}")
                return []
            
            files = []
            for filename in os.listdir(self.base_path):
                if filename.endswith('.md') and os.path.isfile(os.path.join(self.base_path, filename)):
                    files.append(filename)
            
            logger.debug(f"Found {len(files)} SOP files in local directory: {self.base_path}")
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Error listing local SOP files: {e}")
            return []
    
    def _list_s3_files(self) -> List[str]:
        """List SOP files from S3 storage."""
        try:
            response = self._s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=self.s3_prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                # Extract filename from S3 key
                filename = key.replace(self.s3_prefix, '')
                if filename.endswith('.md') and '/' not in filename:  # Only direct files, not subdirectories
                    files.append(filename)
            
            logger.debug(f"Found {len(files)} SOP files in S3 bucket: {self.s3_bucket}")
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Error listing S3 SOP files: {e}")
            return []
    
    def _read_sop_file(self, filename: str) -> Optional[str]:
        """
        Read SOP file content from storage.
        
        Args:
            filename: Name of the SOP file to read
            
        Returns:
            File content as string, or None if error
        """
        if self.use_s3 and self._s3_client:
            return self._read_s3_file(filename)
        else:
            return self._read_local_file(filename)
    
    def _read_local_file(self, filename: str) -> Optional[str]:
        """Read SOP file from local file system."""
        try:
            file_path = os.path.join(self.base_path, filename)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            logger.debug(f"Read local SOP file: {filename}")
            return content
            
        except FileNotFoundError:
            logger.error(f"SOP file not found: {filename}")
            return None
        except Exception as e:
            logger.error(f"Error reading local SOP file {filename}: {e}")
            return None
    
    def _read_s3_file(self, filename: str) -> Optional[str]:
        """Read SOP file from S3 storage."""
        try:
            key = f"{self.s3_prefix}{filename}"
            response = self._s3_client.get_object(Bucket=self.s3_bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            logger.debug(f"Read S3 SOP file: {filename}")
            return content
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"SOP file not found in S3: {filename}")
            else:
                logger.error(f"Error reading S3 SOP file {filename}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading S3 SOP file {filename}: {e}")
            return None
    
    def _parse_sop_metadata(self, content: str, filename: str) -> Dict[str, Any]:
        """
        Parse metadata from SOP markdown content.
        
        Args:
            content: Raw markdown content
            filename: SOP filename
            
        Returns:
            Dictionary containing parsed metadata
        """
        metadata = {
            'name': filename,
            'title': '',
            'document_id': '',
            'version': '',
            'effective_date': '',
            'review_date': '',
            'owner': '',
            'approved_by': '',
            'word_count': len(content.split()),
            'last_modified': datetime.now().isoformat(),
            'storage_location': 's3' if self.use_s3 else 'local'
        }
        
        try:
            # Extract title from first heading
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # Parse document control section
            doc_control_section = re.search(
                r'##\s+Document Control\s*\n(.*?)(?=\n##|\n---|\Z)', 
                content, 
                re.DOTALL | re.IGNORECASE
            )
            
            if doc_control_section:
                control_content = doc_control_section.group(1)
                
                # Extract metadata fields using regex patterns
                patterns = {
                    'document_id': r'\*\*Document ID:\*\*\s*(.+?)(?:\n|$)',
                    'version': r'\*\*Version:\*\*\s*(.+?)(?:\n|$)',
                    'effective_date': r'\*\*Effective Date:\*\*\s*(.+?)(?:\n|$)',
                    'review_date': r'\*\*Review Date:\*\*\s*(.+?)(?:\n|$)',
                    'owner': r'\*\*Owner:\*\*\s*(.+?)(?:\n|$)',
                    'approved_by': r'\*\*Approved By:\*\*\s*(.+?)(?:\n|$)'
                }
                
                for field, pattern in patterns.items():
                    match = re.search(pattern, control_content, re.IGNORECASE)
                    if match:
                        metadata[field] = match.group(1).strip()
            
            # Parse sections for structure analysis
            sections = []
            section_matches = re.finditer(r'^##\s+(\d+\.?\s*)?(.+)$', content, re.MULTILINE)
            
            for match in section_matches:
                section_number = match.group(1).strip() if match.group(1) else ''
                section_title = match.group(2).strip()
                
                # Find subsections
                subsections = []
                subsection_pattern = rf'###\s+{re.escape(section_number)}\.(\d+)\s+(.+)$'
                subsection_matches = re.finditer(subsection_pattern, content, re.MULTILINE)
                
                for sub_match in subsection_matches:
                    subsection_num = f"{section_number}.{sub_match.group(1)}"
                    subsection_title = sub_match.group(2).strip()
                    subsections.append(f"{subsection_num} {subsection_title}")
                
                sections.append({
                    'number': section_number,
                    'title': section_title,
                    'subsections': subsections
                })
            
            metadata['sections'] = sections
            
        except Exception as e:
            logger.warning(f"Error parsing metadata for {filename}: {e}")
        
        return metadata
    
    def load_sops(self, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Load all SOP documents with metadata and content.
        
        Args:
            force_refresh: Force reload even if cache is valid
            
        Returns:
            Dictionary mapping filename to SOP data
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid() and self._sop_cache:
            logger.debug("Returning cached SOP data")
            return self._sop_cache
        
        logger.info("Loading SOP documents from storage")
        sops = {}
        
        try:
            filenames = self._list_sop_files()
            
            for filename in filenames:
                content = self._read_sop_file(filename)
                if content:
                    metadata = self._parse_sop_metadata(content, filename)
                    
                    sops[filename] = {
                        **metadata,
                        'content': content,
                        'metadata': {
                            'file_size': len(content.encode('utf-8')),
                            'last_modified': datetime.now().isoformat(),
                            'word_count': metadata['word_count'],
                            'storage_location': metadata['storage_location']
                        }
                    }
                else:
                    logger.warning(f"Failed to load SOP file: {filename}")
            
            # Update cache
            self._sop_cache = sops
            self._cache_timestamp = datetime.now()
            
            logger.info(f"Successfully loaded {len(sops)} SOP documents")
            
        except Exception as e:
            logger.error(f"Error loading SOPs: {e}")
            # Return cached data if available, otherwise empty dict
            return self._sop_cache if self._sop_cache else {}
        
        return sops
    
    def get_sop_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific SOP by filename.
        
        Args:
            name: SOP filename (e.g., "emergency-procurement-sop.md")
            
        Returns:
            SOP data dictionary or None if not found
        """
        sops = self.load_sops()
        return sops.get(name)
    
    def get_sop_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific SOP by document control ID.
        
        Args:
            document_id: Document ID (e.g., "SOP-PROC-001")
            
        Returns:
            SOP data dictionary or None if not found
        """
        sops = self.load_sops()
        
        for sop_data in sops.values():
            if sop_data.get('document_id', '').upper() == document_id.upper():
                return sop_data
        
        return None
    
    def search_sops(self, keyword: str, search_in: str = "all") -> List[Dict[str, Any]]:
        """
        Search SOPs by keyword.
        
        Args:
            keyword: Search term
            search_in: Where to search - "title", "content", or "all"
            
        Returns:
            List of matching SOPs with relevance information
        """
        if not keyword.strip():
            return []
        
        sops = self.load_sops()
        results = []
        keyword_lower = keyword.lower()
        
        for sop_data in sops.values():
            matches = []
            total_matches = 0
            
            # Search in title
            if search_in in ["title", "all"]:
                title = sop_data.get('title', '').lower()
                title_matches = title.count(keyword_lower)
                if title_matches > 0:
                    matches.append({
                        'section': 'Title',
                        'text': sop_data.get('title', ''),
                        'match_count': title_matches
                    })
                    total_matches += title_matches
            
            # Search in content
            if search_in in ["content", "all"]:
                content = sop_data.get('content', '').lower()
                content_matches = content.count(keyword_lower)
                
                if content_matches > 0:
                    # Find excerpts around matches
                    excerpts = self._extract_excerpts(sop_data.get('content', ''), keyword, max_excerpts=3)
                    
                    for excerpt in excerpts:
                        matches.append({
                            'section': excerpt.get('section', 'Content'),
                            'text': excerpt['text'],
                            'match_count': excerpt['match_count']
                        })
                    
                    total_matches += content_matches
            
            # Add to results if matches found
            if total_matches > 0:
                # Calculate relevance score (simple scoring based on match count and location)
                relevance_score = min(total_matches / 10.0, 1.0)  # Normalize to 0-1
                
                # Boost score for title matches
                title_matches = sum(m['match_count'] for m in matches if m['section'] == 'Title')
                if title_matches > 0:
                    relevance_score = min(relevance_score + 0.3, 1.0)
                
                results.append({
                    'name': sop_data['name'],
                    'title': sop_data.get('title', ''),
                    'document_id': sop_data.get('document_id', ''),
                    'relevance_score': round(relevance_score, 2),
                    'total_matches': total_matches,
                    'excerpts': matches[:5]  # Limit excerpts
                })
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results
    
    def _extract_excerpts(self, content: str, keyword: str, max_excerpts: int = 3, context_chars: int = 150) -> List[Dict[str, Any]]:
        """
        Extract text excerpts around keyword matches.
        
        Args:
            content: Full text content
            keyword: Search keyword
            max_excerpts: Maximum number of excerpts to return
            context_chars: Characters of context around each match
            
        Returns:
            List of excerpt dictionaries
        """
        excerpts = []
        keyword_lower = keyword.lower()
        content_lower = content.lower()
        
        # Find all match positions
        positions = []
        start = 0
        while True:
            pos = content_lower.find(keyword_lower, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        # Extract excerpts around matches
        used_ranges = []
        
        for pos in positions[:max_excerpts * 2]:  # Get more than needed to filter overlaps
            # Calculate excerpt boundaries
            start_pos = max(0, pos - context_chars)
            end_pos = min(len(content), pos + len(keyword) + context_chars)
            
            # Check for overlap with existing excerpts
            overlaps = any(
                not (end_pos <= r[0] or start_pos >= r[1])
                for r in used_ranges
            )
            
            if not overlaps and len(excerpts) < max_excerpts:
                excerpt_text = content[start_pos:end_pos].strip()
                
                # Try to find section context
                section_name = self._find_section_for_position(content, pos)
                
                # Count matches in this excerpt
                match_count = excerpt_text.lower().count(keyword_lower)
                
                excerpts.append({
                    'section': section_name or 'Content',
                    'text': f"...{excerpt_text}..." if start_pos > 0 or end_pos < len(content) else excerpt_text,
                    'match_count': match_count
                })
                
                used_ranges.append((start_pos, end_pos))
        
        return excerpts
    
    def _find_section_for_position(self, content: str, position: int) -> Optional[str]:
        """Find the section heading that contains the given position."""
        try:
            # Find all section headings before the position
            headings = []
            for match in re.finditer(r'^(#{1,3})\s+(.+)$', content[:position], re.MULTILINE):
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append((level, title, match.start()))
            
            # Return the most recent heading
            if headings:
                return headings[-1][1]
            
        except Exception:
            pass
        
        return None
    
    def list_sops(self) -> List[Dict[str, Any]]:
        """
        Get list of all SOPs with basic metadata.
        
        Returns:
            List of SOP metadata dictionaries
        """
        sops = self.load_sops()
        
        sop_list = []
        for sop_data in sops.values():
            sop_list.append({
                'name': sop_data['name'],
                'title': sop_data.get('title', ''),
                'document_id': sop_data.get('document_id', ''),
                'version': sop_data.get('version', ''),
                'effective_date': sop_data.get('effective_date', ''),
                'owner': sop_data.get('owner', ''),
                'word_count': sop_data.get('word_count', 0),
                'storage_location': sop_data.get('storage_location', 'unknown')
            })
        
        # Sort by name
        sop_list.sort(key=lambda x: x['name'])
        
        return sop_list
    
    def refresh_cache(self):
        """Force refresh of the SOP cache."""
        logger.info("Forcing SOP cache refresh")
        self.load_sops(force_refresh=True)
    
    def clear_cache(self):
        """Clear the SOP cache."""
        logger.info("Clearing SOP cache")
        self._sop_cache.clear()
        self._cache_timestamp = None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache state.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_sops': len(self._sop_cache),
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            'cache_valid': self._is_cache_valid(),
            'cache_ttl_seconds': self._cache_ttl_seconds,
            'storage_mode': 's3' if self.use_s3 else 'local',
            'base_path': self.base_path,
            's3_bucket': self.s3_bucket if self.use_s3 else None,
            's3_prefix': self.s3_prefix if self.use_s3 else None
        }

# Global instance for easy access
sop_data_loader = SOPDataLoader()